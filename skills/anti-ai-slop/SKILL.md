---
name: anti-ai-slop
description: Strip AI-tell words, phrases, punctuation, and structural tics out of writing so it doesn't read as LLM-generated. Use when writing or editing prose, docs, READMEs, commit messages, PR descriptions, blog posts, emails, or Slack messages, and when the user asks to "de-slop", "make it sound human", "remove AI tells", or "edit this text".
---

# Anti AI Slop

A banlist plus the rewrite rules that make the banlist usable. The point is not to
find synonyms for banned words. It's to cut the sentence that needed them.

## How to use this skill

1. **Draft normally**, then pass the draft against the lists below.
2. **For every hit, delete before you substitute.** Most slop phrases are filler;
   removing them loses no information. Only reach for a replacement when the
   sentence genuinely carries meaning.
3. **Check the structural tics** (below). They're a bigger tell than any single
   word. A paragraph with zero banned words can still read as AI-generated if
   every sentence is the same length and every list has exactly three items.
4. **Read the result aloud.** If you wouldn't say it to a colleague, cut it.

When editing someone else's text, change only what's on the list plus what's
needed to keep the sentence grammatical. Don't rewrite their voice.

---

## Banned words

Single words that flag machine authorship. Delete or replace with the plain word
in parentheses.

| Word | Use instead |
|------|-------------|
| delve | look at, dig into, or just cut |
| leverage (as a verb) | use |
| utilize | use |
| showcase | show |
| harness (as a verb) | use |
| facilitate | help, let |
| streamline | simplify, speed up |
| robust | (say what's actually true: tested, handles X) |
| seamless / seamlessly | (cut) |
| effortless / effortlessly | (cut) |
| comprehensive | complete, or name the scope |
| holistic | (cut) |
| nuanced | (cut, or state the nuance) |
| multifaceted | (cut) |
| myriad | many |
| plethora | many, a lot of |
| landscape (figurative) | (cut) |
| realm | (cut) |
| tapestry | (cut) |
| ecosystem (non-technical) | (cut) |
| journey (non-literal) | (cut) |
| unlock (figurative) | (cut) |
| elevate | improve, or cut |
| empower | let, help |
| supercharge | speed up |
| revolutionize / game-changing | (cut) |
| cutting-edge / state-of-the-art | (cut, or cite the benchmark) |
| bespoke | custom |
| curated | chosen, or cut |
| meticulous / meticulously | careful, or cut |
| pivotal | important, or cut |
| paramount | most important |
| crucial / vital | important, needed |
| profound | big, or cut |
| testament (a testament to) | shows |
| underscore / underscores | shows, means |
| resonate | (cut) |
| align / alignment (non-technical) | match, agree |
| synergy | (cut) |
| paradigm | model, approach |
| granular | detailed, specific |
| actionable | (cut) |
| impactful | (cut: say what the impact was) |
| load-bearing (figurative) | (cut: say what actually depends on it) |
| foundational | basic, or cut |
| non-trivial | hard, or say how hard |
| arguably | (cut) |
| notably / importantly | (cut) |
| essentially / fundamentally / ultimately | (cut) |
| simply / just / merely | (cut: usually condescending) |
| various | (cut, or name them) |
| several / numerous | a number you actually know |
| significant | (cut, or give the number) |

## Banned phrases

Openers, transitions, and closers that exist only to fill space.

**Openers**
- "Let's dive in" / "Let's dive into" / "Let's jump right in"
- "In today's fast-paced world"
- "In the ever-evolving landscape of"
- "Have you ever wondered"
- "Picture this"
- "Buckle up"
- "Here's the thing"
- "Great question!"
- "You're absolutely right"
- "I'd be happy to help"

**Transitions and hedges**
- "It's worth noting that"
- "It's important to note that"
- "That said" (as a reflex, not a real turn)
- "At the end of the day"
- "When it comes to"
- "In terms of"
- "As we've seen"
- "Needless to say"
- "The key takeaway is"
- "Let's break it down"
- "Let's unpack that"
- "Think of it as"

**The X-not-Y construction**, the single loudest tell:
- "It's not just X, it's Y"
- "This isn't about X — it's about Y"
- "Not only ... but also"
- "X isn't a bug, it's a feature" (and every variant)
- "smoking footgun" (and its cousins: "smoking gun of footguns", "foot-cannon")

**Closers**
- "In conclusion"
- "In summary" (in anything under 2000 words)
- "The possibilities are endless"
- "Only time will tell"
- "Whether you're a beginner or an expert"
- "Happy coding!"
- "I hope this helps!"
- "Let me know if you have any questions"

**Tech-writing specific**
- "under the hood"
- "out of the box"
- "first-class citizen"
- "single source of truth" (unless it's literally a data-modeling claim)
- "battle-tested"
- "production-ready" (unless you define what that means here)
- "blazingly fast"
- "dead simple"
- "sane defaults"
- "it just works"
- "rich set of features"
- "powerful and flexible"

## Banned characters and punctuation

| Character | Why | Do this |
|-----------|-----|---------|
| — (em dash) | The #1 visual tell. Overused as a universal connector. | Use a period, comma, colon, or parentheses. At most one per document, and only where nothing else fits. |
| – (en dash used as a connector) | Same tell, thinner. | Same fix. En dashes are for number ranges only (10–20). |
| ’ “ ” (curly quotes) | Comes from copy-pasting model output. | Straight quotes: ' and ". Mandatory in code and config. |
| … (ellipsis character) | Same source. | Three periods, or cut the trailing-off. |
| → ⇒ ⟶ (arrow glyphs in prose) | Reads as slide deck. | "to", "becomes", "then". Fine in diagrams and code. |
| ✅ ❌ 🚀 ✨ 🎯 🔥 💡 (decorative emoji) | Emoji as bullet points or section badges. | Plain bullets. Emoji only where the user already uses them. |
| **Bold** on every other phrase | Emphasis inflation, nothing stands out. | Bold at most one thing per paragraph, usually zero. |
| Header emoji + title case on every H2 | Template smell. | Sentence-case headers, no emoji. |

## Structural tics

Harder to spot than words, and a stronger signal.

- **Rule of three everywhere.** Every list has exactly three items; every sentence
  has three clauses. Real lists are 2, 4, 7 items long. Vary them.
- **Uniform sentence length.** All sentences land at 15–20 words. Mix a
  four-word sentence in.
- **Every paragraph is three sentences.** Vary it. One-sentence paragraphs are fine.
- **Restating the question before answering.** Just answer.
- **Summarizing what you just said.** If it's one screen long, no recap.
- **Announcing structure.** "First, I'll cover X. Then Y." Just cover X.
- **Symmetric bullets.** Every bullet the same length with the same
  `**Bold term** — explanation` shape. Break the pattern.
- **Hedged everything.** "may", "can", "might", "generally" on every claim.
  Say the thing, or say you don't know.
- **Praise sandwich.** Compliment, content, compliment. Cut both slices.
- **Fake enthusiasm.** Exclamation points on statements of fact.

## What good looks like

Slop:
> It's worth noting that this approach doesn't just streamline the workflow — it
> fundamentally revolutionizes how teams leverage their existing ecosystem to
> unlock seamless collaboration. Let's dive into the details! 🚀

Clean:
> This cuts the deploy step from four commands to one. Details below.

Slop:
> The caching layer is a crucial, load-bearing component that showcases a robust,
> comprehensive approach to performance optimization.

Clean:
> Every request hits the cache first. If it's down, page loads go from 40ms to
> 900ms.

## Adding to the list

Add entries to the table or bullet list that matches the kind of tell:

- A single word → **Banned words** table, with a plain replacement in the second
  column (or `(cut)` if the word is pure filler).
- A multi-word construction → **Banned phrases**, under the sub-heading that fits
  (opener / transition / X-not-Y / closer / tech-writing).
- Punctuation or a glyph → **Banned characters and punctuation** table, with why
  it reads as machine output and what to use instead.
- A shape or rhythm rather than a string → **Structural tics**.

Keep entries short and give a replacement, not just a prohibition. A banlist with
no alternative just produces slop with different words.
