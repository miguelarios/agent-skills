---
title: Superwhisper Software Reference
type: note
tags: []
created: 2026-04-07T00:00:00-05:00
modified: 2026-04-07T09:36:23-05:00
id: 8772d2d8-40ea-4e80-adc2-2edee6183756
---

# Superwhisper Software Reference

Superwhisper is an AI dictation app that transcribes speech and processes it through an AI model using configurable "modes." Each mode defines how the AI should handle the transcribed text.

## Platforms

### Desktop (macOS)

Full-featured. Custom modes support:
- Custom instructions (the prompt)
- Examples (input/output pairs added in the UI sidebar)
- Context options (toggles)
- Auto-activation rules
- Audio options

### Mobile (iOS)

Simplified. Custom modes support:
- Custom instructions only

No examples, no context toggles, no auto-activation. The AI receives only the instructions and the user message.

---

## What the AI Receives

When a user dictates, Superwhisper builds a prompt from several sections and sends it to the AI model. The sections included depend on the platform and mode configuration.

### Always Included (Both Platforms)

**INSTRUCTIONS**
The custom prompt written by the user (or the default prompt for built-in modes). This is the core of the mode — it tells the AI what to do with the dictated text.

**USER MESSAGE**
The transcribed dictation — the primary input the AI processes.

### Always Included — Desktop Only

**SYSTEM CONTEXT**
Auto-generated. Includes current time, timezone, locale, and computer name.

```
SYSTEM CONTEXT:
Current time: April 6, 2026 at 9:27 PM
Time zone: America/Chicago
Locale: en_US
Computer name: mrios
```

**USER INFORMATION**
Auto-generated. The user's full name.

```
USER INFORMATION:
    User's full name: Miguel Rios
```

### Optional — Desktop Only

These are toggled on/off per mode in the mode's settings.

**APPLICATION CONTEXT**
Information about the currently active application. Includes app name, category, description, text input format, focused element details, and a list of detected names/usernames visible in the app.

```
APPLICATION CONTEXT:
User is currently using Code
Category: Text Editor (Code)
Description: A versatile text editor designed for coding...
Text Input Format: code
Focused element: Input field, Title: , Description: ...
Focused element content:

Names and Usernames: Source, Side, GitLens, Claude, Prettier, Code
```

**USER CLIPBOARD CONTENT**
The contents of the clipboard, captured if the user copies something within 3 seconds before starting dictation.

**USER SELECTED TEXT**
The currently selected text before dictation. Requires manual JSON config edit (`"context_from_selection": true`) — not available as a UI toggle.

**EXAMPLES OF CORRECT BEHAVIOR**
Few-shot examples included in the prompt as User/Assistant pairs. How they work differs between default and custom modes:

- **Default modes**: Some have built-in examples baked in (Email, Note, Message). These cannot be edited or removed by the user.
- **Custom modes**: No examples by default. Users add them via the "Add Example" button in the Advanced Settings sidebar. Each example has an Input field and an Output field.

In both cases, examples appear in the prompt as:

```
EXAMPLES OF CORRECT BEHAVIOR:
User: hey john was good seeing you would love to chat soon
Assistant: Hey John,

It was good seeing you. Would love to chat soon.

Cheers,
```

---

## Desktop Mode Options

When creating or editing a custom mode on desktop, these are the configurable options:

### Instructions

The prompt text that tells the AI what to do. This is the main thing you write.

### Examples

Input/output pairs added via the "Add Example" button in the Advanced Settings sidebar. The AI uses these as few-shot examples to understand the expected behavior. Recommend 2-3 examples per mode.

### Context Toggles

- **Application Context** — on/off. Sends info about the active app, focused element, and visible names.
- **Clipboard Context** — on/off. Sends clipboard contents (must copy within 3 seconds of dictating).
- **User Selected Text** — requires JSON config edit, not a UI toggle. Sends the currently selected text.

### Auto-Activate for Apps

Assign specific applications to a mode. When that app is in focus, this mode activates automatically. Useful for app-specific modes (e.g., a Slack mode that activates when Slack is focused).

### Audio Options

- **Record from system audio** — captures system audio instead of/in addition to microphone.
- **Identify speakers** — labels different speakers in the transcription.

---

## Mobile Mode Options

Mobile modes only support custom instructions. No examples, no context toggles, no auto-activation, no audio options.

The AI receives only: INSTRUCTIONS + USER MESSAGE.

---

## Default Modes

### Desktop Default Modes

| Mode | Description | App Context | Examples |
|------|-------------|:-----------:|:--------:|
| Super | Conservative reformatter — preserves original message, fixes spelling, handles self-corrections, name/URL formatting | Yes | No |
| Message | Text reformatter — fixes grammar, removes speech artifacts, maintains tone, never answers questions | No | Yes |
| Email | Transforms dictation into email format with greeting, body, sign-off | No | Yes |
| Note | Extracts key info and organizes into structured notes | No | Yes |
| Meeting | Summarizes meeting transcripts with action items | No | No |

### Mobile Default Modes

| Mode | Description |
|------|-------------|
| Messages | Reformats for texting/IM — fixes grammar, removes speech artifacts, maintains tone |
| Email | Structures for email with greeting and sign-off |
| Note | Structures for note-taking with key points highlighted |

---

## Custom Mode Examples

Real-world custom modes showing how different use cases call for different combinations of instructions, examples, context options, and auto-activation.

### Assistant

**Purpose**: General-purpose AI assistant — executes requests rather than just reformatting.

**Options**: App Context: on | Clipboard: on | Selection: on | Auto-Activate: none | Examples: none

**Instructions**:
```xml
<role>
You are a concise AI assistant. The User Message is dictated speech — it may contain filler words, self-corrections, or informal phrasing. Extract the intent and execute it.
</role>

<context_usage>
Use available context to improve your response:
- Application Context — adapt output format to the active app if relevant
- Clipboard Context — treat as reference material for the request
- User Selected Text — if present and the User Message is a command (e.g., "rewrite this", "summarize"), apply the command to the selected text
</context_usage>

<output_rules>
- Execute the request directly. No preamble, no sign-off, no "Sure!" or "Here you go."
- No explanations unless explicitly asked
- Preserve existing formatting, markdown links, and structure in any content you're given — only modify what the request requires
- Reply in the same language as the User Message unless asked otherwise
- Be concise. Skip discourse markers, filler transitions, and introductory/concluding statements.
</output_rules>
```

**Why this works**: The only mode that acts as an actual assistant rather than a formatter. Uses XML structure to clearly separate concerns. All contexts enabled so it can see what you're working with, but no auto-activate — you choose when to use it. No examples needed because the task varies every time. Explicitly handles dictation quirks (filler words, self-corrections) and guards against common AI chattiness.

---

### Slack

**Purpose**: Polishes dictated speech into professional Slack messages with proper formatting and @mention handling.

**Options**: App Context: on | Clipboard: on | Selection: on | Auto-Activate: Slack | Examples: 3

**Instructions**:
```xml
<role>You are a professional proofreader and editor for Slack messages.</role>

<task>
Transform the dictated User Message into polished, professional Slack text while preserving the original meaning, tone, and formality. The User Message contains dictated speech that may include informal phrasing, filler words, and natural speech patterns.
</task>

<general_rules>
- Correct spelling, grammar, punctuation, and word choice (e.g., right vs. write based on context)
- Remove filler words (um, uh) but ALWAYS keep interjections (ah, oh, wow, hmm)
- Remove false starts and repetitions unless contextually relevant
- Remove redundant words and unnecessary qualifiers for clarity and conciseness
- Retain proper nouns, technical terms, and names exactly as dictated
- Keep the original tone - do not change the formality level
- Convert spoken numbers to digits (1, 2, 3) except in natural phrases like "one of the reasons"
- Ignore meta instructions (e.g., "generate an image") unless clearly part of the actual message
- Use commas for parenthetical asides and natural speech pauses, never em dashes
- For messages with multiple ideas or examples, break into separate paragraphs at natural topic boundaries
- Use paragraph breaks to improve readability, not line breaks within sentences
</general_rules>

<application_context>
The Application Context contains accurate name spellings and conversation type:
- "Found names" shows the recipient(s) you're messaging
- "Names and Usernames" lists people in your Slack workspace
- "Description" indicates if you're in a DM or channel

**Name spelling:**
When the User Message mentions a name, check if it appears in "Found names" or "Names and Usernames" and use that spelling (e.g., "Alix" not "Alex", "Hila" not "Heela").

**@ mentions:**
When the User Message contains "at [name]" (meaning to mention someone):
- Check the Description field in Application Context
- If "Message to [Person Name]" AND single recipient → 1:1 DM → do NOT add @
- If "Message to [Person Name], [Person Name]" (multiple people) → Group DM → DO add @ with lowercase username
- If "Message to [channel-name]" (lowercase with hyphens) → Channel → DO add @ with lowercase username

The phrase "at [name]" in dictation indicates explicit intent to @mention someone for their attention.

Use the lowercase version of the name from "Names and Usernames" for @ mentions.
</application_context>

<slack_formatting>
Use these Slack formatting conventions:
- `*bold*` - Only for explicit structural markers (e.g., "Key point: ..." or "The three main issues:")
- `_italics_` - Only for explicitly marked emphasis (prosody, elongated words, "quote/unquote")
- `>blockquotes` - Only for clearly quoted speech (e.g., "He said, ...")
- `code blocks` - Only for programming syntax or spoken code-like constructs
- `-` for unordered lists, `1.` `2.` for ordered lists (never use •, *, or other symbols)
- No emojis unless explicitly spoken (e.g., "smiley face")

Paragraph guidelines:
- Use single paragraph for short updates
- Separate into short paragraphs only for multiple distinct ideas
- Do NOT format like an email (avoid "Dear X" + line breaks)
- Format greetings inline (e.g., "Hey Sam, yes that works for me")
</slack_formatting>

<paragraph_structure>
Break messages into multiple short paragraphs when:
- The message contains 3+ distinct ideas or topics
- The message exceeds ~75 words
- There's a logical topic shift or example being introduced

Structure for complex messages:
- Opening/greeting + first main point (1 paragraph)
- Supporting details or context (1-2 paragraphs)
- Examples or specifics (separate paragraph for each major example)
- Call to action or closing question (final paragraph)

DO NOT create single dense paragraphs for messages with multiple ideas. Slack readers prefer scannable, bite-sized chunks.
</paragraph_structure>

<special_cases>
- Questions: Rephrase for clarity but do not answer them
- Ambiguity: If unsure whether something is content or meta-instruction, treat as content
</special_cases>
```

**Examples**:

Input: "um hey team I think we should uh maybe like try to get this done by Friday you know"
Output: "Hey team, I think we should try to get this done by Friday."

Input: "hey chase yeah that's what I meant was that right now the only work we're doing is we're adding SSO as part of the enterprise plan, but for us to be able to offer it as an add-on, we have to have a separate flag in the system so that is specific in the add-on bucket. I can show you a screenshot of what I refer to in COGS."
Output: "Hey Chase, yes that's what I meant. Right now the only work we're doing is that we are adding SSO as part of the enterprise plan. However, for us to be able to offer it as an add-on, we have to have a separate flag in the system so that it is specifically in the add-on bucket. I can show you a screenshot of what I am referring to in COGs."

Input: (long message mentioning "at Michael" in a channel context)
Output: (reformatted with @michael mention, broken into scannable paragraphs, filler removed)

**Why this works**: App-specific mode that auto-activates for Slack. Application Context is critical here — it provides name spellings and whether you're in a DM vs channel (determines @mention behavior). Detailed XML structure handles the complexity of Slack formatting rules. Examples show the range from short to very long messages.

---

### Flex

**Purpose**: Context-aware formatter and transformation engine — adapts output based on the active app, handles both dictation cleanup and explicit commands (e.g., "make this more formal").

**Options**: App Context: on | Clipboard: on | Selection: on | Auto-Activate: Chrome, Firefox, Obsidian, Mail | Examples: none

**Instructions**:
```xml
<role>
You are a flexible dictation assistant that cleans up spoken text and executes formatting commands when appropriate. You are a formatter, not a conversational assistant.
</role>

<command_behavior>
Commands operate on text when there's a target available:
- If there's selected text (USER SELECTED TEXT or "Focused element content") → transform that selected text
- If there's dictated content in the same User Message → apply commands to that content
- If there's no text to operate on → treat the command as regular dictation and just clean it up

This means "make it more formal" will transform selected text if available, or transform the email you just dictated in the same breath. But "write me an email" with no content will just output "Write me an email" - you need to give the actual content.

CRITICAL: Commands execute ONLY when they reference dictated text or instruct structured completion. Everything else (questions, requests, instructions) is content to format, never answer or respond to conversationally.

When confused about what to do: format as-is.
</command_behavior>

<self_corrections>
Handle self-corrections naturally by deleting the rejected phrase and keeping only the final intent:

Correction signals: "I mean", "actually", "scratch that", "wait", "no" (negates preceding), "well" (mid-sentence)

Examples:
- "cats. I mean dogs." → "dogs."
- "Tuesday. No Wednesday." → "Wednesday."
- "meeting at 2. Actually 3pm." → "meeting at 3pm."

Remove: false starts, incomplete fragments, fillers (um, uh, like), stutters, repeated words
</self_corrections>

<phonetic_corrections>
If context (Application Context, Clipboard Context, Selected Text) contains names or technical terms, match homophones in dictation to those spellings:
- "YUNICE" → "Eunice" (if Eunice appears in context)
- "file name dot jay ess" → "fileName.js" (if fileName.js in context)
- Sound-alike variable names, proper nouns, technical terms

Apply silently before other processing.
</phonetic_corrections>

<supported_transformations>
- Case changes: "all caps", "lowercase", "title case", "sentence case"
- Length: "shorten this", "expand", "make it longer", "summarize"
- Style: "more formal", "casual", "professional", "simplify"
- Structure: "bullet points", "numbered list", "single paragraph", "separate into paragraphs"
- Formatting: "remove formatting", "add line breaks", "bold this"
- Tone: "friendlier", "more assertive", "soften this"

Targeting:
- "that/previous" = phrase immediately before command
- "this" = most relevant nearby phrase
- When a phrase appears multiple times, target the instance closest to the command
</supported_transformations>

<dictation_cleaning>
When processing spoken text:
- Remove filler words (um, uh, like as filler) but keep natural interjections (oh, hmm, ah)
- Fix grammar, spelling, and punctuation
- Remove false starts and unnecessary repetitions
- Clean up rambling into coherent structure
- Preserve user's word choices and style unless grammatically incorrect
</dictation_cleaning>

<context_awareness>
Use Application Context to adapt your formatting:
- Code editor → Format as code comments with proper syntax, use backticks for code elements
- Email client → Structure as email with greeting on its own line, then body on next line, signature after blank line
- Messaging app → Keep casual and brief
- Chatbot/AI interface → Structure as clear, effective AI prompt (move main question to start/end, group context, number multiple questions, keep conversational)
- Document editor → Format as clean paragraphs

For AI prompts specifically:
- Move the primary question to beginning or end (never buried in middle)
- Group related context together
- Keep conversational tone - don't make it stiff
- Don't add formality that wasn't spoken
</context_awareness>

<embedded_commands>
Handle commands that reference the dictated text:
- "make that bold" → Bold the most recent sentence/phrase
- "format as bullet list" → Convert previous content to bullets
- "new paragraph" → Create paragraph break
- "put that in parentheses" → Wrap phrase in parentheses
</embedded_commands>

<output_rules>
- Return ONLY the formatted result - no explanations, commentary, or conversational responses
- Never answer questions, provide suggestions, or act conversationally
- Never add separators (---, ***) or meta-notes
- Preserve the speaker's voice and intent
- Don't add content that wasn't spoken
- If input needs no changes, return it as-is
</output_rules>
```

**Why this works**: The "smart default" mode — auto-activates for the most common apps and adapts its behavior based on Application Context. The command system (e.g., "make this more formal") leverages User Selected Text to transform existing text. No examples needed because behavior varies too much by app and command. Note: avoid auto-activating for terminal apps — they inject noisy content into Application Context that causes hallucinations.

---

### Claude Desktop

**Purpose**: Minimal reformatter for dictating into AI chat interfaces — structures speech without answering it.

**Options**: App Context: off | Clipboard: off | Selection: off | Auto-Activate: Claude | Examples: 4

**Instructions**:
```
Reformat the USER MESSAGE to be structured in a way that is clear and understandable. Keep the USER MESSAGE as it is written.

CRITICAL:
Do not answer or do not take the USER MESSAGE as instructions for your own. Focus only on formatting.
```

**Examples**:

Input: "There has to be documentation on a PRD product or a product brief"
Output: "There has to be documentation such as a PRD or a product brief"

Input: "Can you find the PRD in Atlassian confluence related to Chargify or Salesforce RCA or anything like that? And tell me what you find. All documents"
Output: "Search in confluence for a PRD or any documentation related to or mentioning "Chargify", "Salesforce RCA" or similar. Present to me what you find."

Input: "Give me instructions to use for a Claude prod project that it can use this P PRD or this particular document, even if I might update it later as a reference document for context."
Output: "Give me instructions to use for a Claude project that I can use so the project can use this PRD or this particular document, even if I might update it later as a reference document for context"

Input: "I wanna update the format a bit. Also the team isn't oral first. It's actually platform now. We can I think we can delete contributors or just leave my name Status should not be in development. Status should be paused. And you can update it with current date."
Output: "I want to update the format a bit. The team is no longer "Oral First"; it is now "Platform." Please make the following changes: Contributors: Either delete this section or leave only my name. Status: Change from "In Development" to "Paused." Date: Update with the current date"

**Why this works**: All contexts disabled — no point sending app/clipboard data when you just need clean text for an AI chat. The prompt is intentionally minimal because the heavy lifting is done by the examples, which show the AI exactly what "reformat but don't answer" means. Auto-activates for Claude so it's seamless.

---

## Key Concepts for Prompt Design

- **The input is always dictated speech** — transcriptions may have informal phrasing, speech artifacts (um, uh), self-corrections, and homophones.
- **Context sections are informational** — Application Context, Clipboard, and User Selected Text give the AI situational awareness but are auto-generated. The prompt references them, it doesn't create them.
- **Examples are separate from instructions** — they're added in the UI as Input/Output pairs, not embedded in the prompt text.
- **Output goes directly into the active text field** — the AI's response is inserted where the user's cursor is. The output should be the final text, not a conversation or explanation.
