# Writing Scripts for Agent Use

Scripts bundled in `scripts/` are run by AI assistants in non-interactive shells. A few design choices make scripts dramatically easier for agents to use effectively.

## Hard Requirement: No Interactive Prompts

Agents cannot respond to TTY prompts, password dialogs, or confirmation menus. A script that blocks on interactive input will hang indefinitely.

Accept all input via command-line flags, environment variables, or stdin:

```
# Bad: hangs waiting for input
$ python scripts/deploy.py
Target environment: _

# Good: clear error with guidance
$ python scripts/deploy.py
Error: --env is required. Options: development, staging, production.
Usage: python scripts/deploy.py --env staging --tag v1.2.3
```

## Document Usage with --help

`--help` output is the primary way an agent learns a script's interface. Include a brief description, available flags, and usage examples:

```
Usage: scripts/process.py [OPTIONS] INPUT_FILE

Process input data and produce a summary report.

Options:
  --format FORMAT    Output format: json, csv, table (default: json)
  --output FILE      Write output to FILE instead of stdout
  --verbose          Print progress to stderr

Examples:
  scripts/process.py data.csv
  scripts/process.py --format csv --output report.csv data.csv
```

Keep it concise — the output enters the agent's context window.

## Write Helpful Error Messages

When an agent gets an error, the message directly shapes its next attempt. Say what went wrong, what was expected, and what to try:

```
Error: --format must be one of: json, csv, table.
       Received: "xml"
```

```
Error: Field 'signature_date' not found.
       Available fields: customer_name, order_total, signature_date_signed
```

Verbose error messages with available options let the agent self-correct without retrying blindly.

## Use Structured Output

Prefer JSON, CSV, or TSV over free-form text. Structured formats can be consumed by both the agent and standard tools (`jq`, `cut`, `awk`).

```
# Bad: whitespace-aligned — hard to parse
NAME          STATUS    CREATED
my-service    running   2025-01-15

# Good: unambiguous field boundaries
{"name": "my-service", "status": "running", "created": "2025-01-15"}
```

**Separate data from diagnostics:** Send structured data to stdout and progress/warnings to stderr. This lets the agent capture clean, parseable output while retaining access to diagnostics.

## Handle Errors Explicitly

Handle error conditions in the script rather than letting them bubble up opaquely:

```python
def process_file(path):
    """Process a file, creating it if it doesn't exist."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        print(f"File {path} not found, creating default", file=sys.stderr)
        with open(path, 'w') as f:
            f.write('')
        return ''
    except PermissionError:
        print(f"Cannot access {path}, using default", file=sys.stderr)
        return ''
```

## Document Constants

Configuration values should be justified, not magical:

```python
# Good: self-documenting
REQUEST_TIMEOUT = 30  # HTTP requests typically complete within 30 seconds
MAX_RETRIES = 3       # Most intermittent failures resolve by second retry

# Bad: magic numbers
TIMEOUT = 47  # Why 47?
RETRIES = 5   # Why 5?
```

## Design for Idempotency

Agents may retry commands. "Create if not exists" is safer than "create and fail on duplicate."

## Support Dry Runs

For destructive or stateful operations, a `--dry-run` flag lets the agent preview what will happen before committing:

```bash
scripts/cleanup.py --dry-run     # Shows what would be deleted
scripts/cleanup.py --confirm     # Actually deletes
```

## Use Meaningful Exit Codes

Use distinct exit codes for different failure types and document them:

```
Exit codes:
  0  Success
  1  Invalid arguments
  2  File not found
  3  Authentication failure
  4  API error
```

## Control Output Size

Many agent harnesses truncate tool output beyond 10-30K characters. If your script might produce large output:

- Default to a summary or reasonable limit
- Support `--offset` and `--limit` for pagination
- Offer `--output FILE` to write full results to a file instead of stdout

## Self-Contained Scripts with Inline Dependencies

When possible, declare dependencies inline so the script runs with a single command and no separate install step.

**Python (PEP 723 + uv):**
```python
# /// script
# dependencies = ["beautifulsoup4>=4.12,<5"]
# ///

from bs4 import BeautifulSoup
# ...
```
Run with: `uv run scripts/extract.py`

**State prerequisites** in SKILL.md (e.g., "Requires Python 3.12+ and uv") or use the `compatibility` frontmatter field for runtime-level requirements.

## Referencing Scripts from SKILL.md

Use relative paths from the skill directory root. List available scripts so the agent knows they exist:

```markdown
## Available scripts

- **`scripts/validate.sh`** — Validates configuration files
- **`scripts/process.py`** — Processes input data and produces summary reports

## Workflow

1. Run validation: `bash scripts/validate.sh "$INPUT_FILE"`
2. Process results: `python3 scripts/process.py --input results.json`
```

**Make execution intent clear:**
- "Run `analyze_form.py` to extract fields" → execute the script
- "See `analyze_form.py` for the extraction algorithm" → read as reference

## When to Bundle vs. Generate

Bundle a script when:
- The same logic is rewritten on every run (check execution transcripts across test cases)
- Deterministic reliability matters
- The operation is fragile or error-prone

Let the agent generate code when:
- The task is genuinely different each time
- The logic is simple and obvious
- Flexibility matters more than consistency
