#!/usr/bin/env python3
"""Pluggable runners for trigger evaluation and description improvement.

A runner answers two questions:

  trigger(query, skill_name, description, ...) -> bool
      Given a realistic user query and a skill listing that contains this
      skill, would the agent consult the skill?
  complete(prompt, model, timeout) -> str
      One-shot text completion (used by improve_description.py).

Runners:
  claude  `claude -p` with a temporary slash-command file so the skill shows
          up in the available-skills list; triggering is detected from real
          Skill/Read tool calls in the stream-json output. Ported from
          Anthropic's skill-creator run_eval.py (Apache-2.0,
          https://github.com/anthropics/skills/tree/main/skills/skill-creator).
  hermes  `hermes chat -Q` with a *simulated* skill index: the model is shown
          the skills listing and asked which skill it would load. This is a
          proxy, not a real tool-call observation. See references/description-optimization.md
          for limits.
  dry     Deterministic keyword-overlap stub. No network, no LLM. Used by
          --dry-run and the tests to exercise the plumbing only; its scores
          say nothing about real triggering.

Stdlib only.
"""

from __future__ import annotations

import json
import os
import re
import select
import subprocess
import tempfile
import time
import uuid
from pathlib import Path


class RunnerError(RuntimeError):
    pass


class Runner:
    name = "base"

    def trigger(self, query: str, skill_name: str, description: str,
                timeout: int, project_root: str, model: str | None = None) -> bool:
        raise NotImplementedError

    def complete(self, prompt: str, model: str | None, timeout: int = 300) -> str:
        raise NotImplementedError


# --------------------------------------------------------------------------
# Claude Code (`claude -p`)
# --------------------------------------------------------------------------

def find_claude_project_root() -> Path:
    """Walk up from cwd looking for .claude/, as Claude Code does."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".claude").is_dir():
            return parent
    return current


class ClaudeRunner(Runner):
    name = "claude"

    @staticmethod
    def _env() -> dict:
        # Allow nesting `claude -p` inside a Claude Code session.
        return {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    def complete(self, prompt, model, timeout=300):
        cmd = ["claude", "-p", "--output-format", "text"]
        if model:
            cmd += ["--model", model]
        result = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                                env=self._env(), timeout=timeout)
        if result.returncode != 0:
            raise RunnerError(f"claude -p exited {result.returncode}\nstderr: {result.stderr}")
        return result.stdout

    def trigger(self, query, skill_name, description, timeout, project_root, model=None):
        clean_name = f"{skill_name}-skill-{uuid.uuid4().hex[:8]}"
        commands_dir = Path(project_root) / ".claude" / "commands"
        command_file = commands_dir / f"{clean_name}.md"
        try:
            commands_dir.mkdir(parents=True, exist_ok=True)
            indented = "\n  ".join(description.split("\n"))
            command_file.write_text(
                f"---\ndescription: |\n  {indented}\n---\n\n# {skill_name}\n\n"
                f"This skill handles: {description}\n"
            )
            cmd = ["claude", "-p", query, "--output-format", "stream-json",
                   "--verbose", "--include-partial-messages"]
            if model:
                cmd += ["--model", model]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                       cwd=project_root, env=self._env())
            return self._watch(process, clean_name, timeout)
        finally:
            if command_file.exists():
                command_file.unlink()

    @staticmethod
    def _watch(process, clean_name: str, timeout: int) -> bool:
        triggered = False
        start = time.time()
        buffer = ""
        pending_tool = None
        acc = ""
        try:
            while time.time() - start < timeout:
                if process.poll() is not None:
                    rest = process.stdout.read()
                    if rest:
                        buffer += rest.decode("utf-8", errors="replace")
                    break
                ready, _, _ = select.select([process.stdout], [], [], 1.0)
                if not ready:
                    continue
                chunk = os.read(process.stdout.fileno(), 8192)
                if not chunk:
                    break
                buffer += chunk.decode("utf-8", errors="replace")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    etype = event.get("type")
                    if etype == "stream_event":
                        se = event.get("event", {})
                        st = se.get("type", "")
                        if st == "content_block_start":
                            cb = se.get("content_block", {})
                            if cb.get("type") == "tool_use":
                                if cb.get("name") in ("Skill", "Read"):
                                    pending_tool = cb["name"]
                                    acc = ""
                                else:
                                    return False
                        elif st == "content_block_delta" and pending_tool:
                            delta = se.get("delta", {})
                            if delta.get("type") == "input_json_delta":
                                acc += delta.get("partial_json", "")
                                if clean_name in acc:
                                    return True
                        elif st in ("content_block_stop", "message_stop"):
                            if pending_tool:
                                return clean_name in acc
                            if st == "message_stop":
                                return False
                    elif etype == "assistant":
                        for item in event.get("message", {}).get("content", []):
                            if item.get("type") != "tool_use":
                                continue
                            inp = item.get("input", {})
                            if item.get("name") == "Skill" and clean_name in inp.get("skill", ""):
                                triggered = True
                            elif item.get("name") == "Read" and clean_name in inp.get("file_path", ""):
                                triggered = True
                            return triggered
                    elif etype == "result":
                        return triggered
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
        return triggered


# --------------------------------------------------------------------------
# Hermes (`hermes chat -Q`)
# --------------------------------------------------------------------------

def read_skill_listing(skills_dir: Path, exclude: str = "", limit: int = 60) -> list[tuple[str, str]]:
    """Collect (name, description) for sibling skills to use as distractors."""
    try:
        from scripts.utils import parse_skill_md
    except ModuleNotFoundError:
        from utils import parse_skill_md
    out = []
    for md in sorted(Path(skills_dir).glob("*/SKILL.md")):
        try:
            n, d, _ = parse_skill_md(md.parent)
        except Exception:
            continue
        if n and n != exclude and d:
            out.append((n, d))
        if len(out) >= limit:
            break
    return out


_SKILL_ANSWER = re.compile(r'"skill"\s*:\s*(null|"([^"]*)")', re.IGNORECASE)


def parse_skill_answer(text: str) -> str | None:
    """Return the last skill name the model answered with, or None for 'none'."""
    matches = _SKILL_ANSWER.findall(text)
    if not matches:
        return None
    raw = matches[-1][1]
    if not raw or raw.strip().lower() in ("none", "null"):
        return None
    return raw.strip()


class HermesRunner(Runner):
    """Simulated skill-selection via `hermes chat`.

    Hermes puts a skills index (name + description) in the system prompt and
    the model calls skill_view(name) to load one. Observing that for real
    would require installing a temporary skill into the user's skills dir and
    parsing session tool calls. Instead this runner reproduces the decision
    point: it shows the model the index and asks which skill (if any) it would
    load before doing the task. Faster and side-effect free, but a proxy: the
    model knows it is being asked, so it can over-report triggering relative
    to real runs. Use it to compare descriptions against each other, not as an
    absolute trigger rate.
    """

    name = "hermes"

    def __init__(self, distractor_dir: Path | None = None, hermes_bin: str = "hermes",
                 extra_args: list[str] | None = None):
        self.distractor_dir = distractor_dir
        self.hermes_bin = hermes_bin
        # --ignore-rules keeps AGENTS.md/SOUL-style context from steering the answer.
        self.extra_args = extra_args if extra_args is not None else ["--ignore-rules"]

    def _chat(self, prompt: str, model: str | None, timeout: int) -> str:
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
            fh.write(prompt)
            qpath = fh.name
        try:
            cmd = [self.hermes_bin, "chat", "-Q", "--oneshot", "--query-file", qpath, *self.extra_args]
            if model:
                cmd += ["-m", model]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        finally:
            os.unlink(qpath)
        if result.returncode != 0:
            raise RunnerError(f"hermes chat exited {result.returncode}\nstderr: {result.stderr[-500:]}")
        return result.stdout

    def complete(self, prompt, model, timeout=300):
        return self._chat(prompt, model, timeout)

    def build_trigger_prompt(self, query: str, skill_name: str, description: str) -> str:
        entries = [(skill_name, description)]
        if self.distractor_dir:
            entries += read_skill_listing(self.distractor_dir, exclude=skill_name)
        entries.sort(key=lambda e: e[0])
        listing = "\n".join(f"- {n}: {d}" for n, d in entries)
        return (
            "You have these skills available. Each is a bundle of instructions you can "
            "load with skill_view(name) before working.\n\n"
            f"<available_skills>\n{listing}\n</available_skills>\n\n"
            "A user sent this message:\n\n"
            f"<user_message>\n{query}\n</user_message>\n\n"
            "Do not do the task. Decide which single skill you would load first, judging "
            "only from names and descriptions, or none if you could handle it without one. "
            'Reply with exactly one JSON object and nothing else: {"skill": "<name>"} or {"skill": "none"}.'
        )

    def trigger(self, query, skill_name, description, timeout, project_root, model=None):
        text = self._chat(self.build_trigger_prompt(query, skill_name, description), model, timeout)
        chosen = parse_skill_answer(text)
        return bool(chosen) and chosen.lower() == skill_name.lower()


# --------------------------------------------------------------------------
# Dry-run stub
# --------------------------------------------------------------------------

_WORD = re.compile(r"[a-z0-9]{4,}")


class DryRunner(Runner):
    """Keyword overlap. Deterministic, offline, scientifically meaningless."""

    name = "dry"

    def trigger(self, query, skill_name, description, timeout, project_root, model=None):
        d = set(_WORD.findall(description.lower()))
        q = set(_WORD.findall(query.lower()))
        return len(d & q) >= 2

    def complete(self, prompt, model, timeout=300):
        m = re.search(r"<current_description>\s*\"?(.*?)\"?\s*</current_description>", prompt, re.DOTALL)
        base = (m.group(1).strip() if m else "Use when the user asks for this skill.")[:900]
        return f"<new_description>{base} Also use for closely related requests.</new_description>"


def make_runner(name: str, *, distractor_dir: str | None = None) -> Runner:
    if name == "claude":
        return ClaudeRunner()
    if name == "hermes":
        return HermesRunner(Path(distractor_dir) if distractor_dir else None)
    if name == "dry":
        return DryRunner()
    raise ValueError(f"unknown runner: {name} (choose claude, hermes, dry)")
