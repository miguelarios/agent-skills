---
name: markitdown
description: "Convert files to Markdown for LLM processing. Supports PDF, DOCX, XLSX, PPTX, images (OCR), audio (transcription), HTML, EPUB, CSV, JSON, XML, YouTube URLs, and ZIP archives. Use when extracting text from documents, transcribing audio, OCR on images, or preparing files for RAG systems. CLI tool: markitdown <file>"
metadata:
  installed: true
  install_command: "uv tool install 'markitdown[all]'"
---

# MarkItDown

Convert various file formats to Markdown optimized for LLM consumption. Preserves structure (headings, tables, lists) while producing clean, token-efficient output.

## Quick Reference

| Task | Command |
|------|---------|
| Convert file to Markdown | `markitdown document.pdf` |
| Save to file | `markitdown doc.pdf -o output.md` |
| Convert with OCR (images) | `markitdown image.jpg` |
| Transcribe audio | `markitdown audio.wav` |
| YouTube transcript | `markitdown "https://youtube.com/watch?v=ID"` |
| Batch convert | `markitdown archive.zip` |
| Pipe input | `cat file.pdf \| markitdown` |

## Supported Formats

**Documents:** PDF, DOCX, XLSX, XLS, PPTX
**Media:** Images (JPEG, PNG, etc.), Audio (WAV, MP3, etc.)
**Web:** HTML, YouTube URLs, EPUB, RSS
**Data:** CSV, JSON, XML
**Archives:** ZIP (processes all files inside)

## Installation

```bash
# Install with all features
uv tool install 'markitdown[all]'

# Verify installation
markitdown --help
```

## Common Workflows

### Document Conversion

```bash
# Basic conversion (prints to stdout)
markitdown report.pdf

# Save to file
markitdown presentation.pptx -o slides.md

# Convert Excel spreadsheet
markitdown data.xlsx -o data.md
```

### Media Processing

```bash
# Image with OCR and EXIF metadata
markitdown scan.jpg -o scan.md

# Audio transcription
markitdown meeting.wav -o transcript.md
```

### Web Content

```bash
# YouTube video transcript
markitdown "https://youtube.com/watch?v=dQw4w9WgXcQ"

# HTML to Markdown
markitdown webpage.html -o page.md
```

### Batch Processing

```bash
# Process all files in a ZIP archive
markitdown documents.zip -o all-docs.md

# Directory conversion (use with find)
find . -name "*.pdf" -exec markitdown {} -o {}.md \;
```

## Python API

For programmatic use within scripts:

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("document.pdf")
print(result.text_content)
```

**See references/python_api.md** for:
- Azure Document Intelligence integration
- LLM-powered image descriptions
- Custom plugin development
- Advanced configuration options

## Error Handling

**Common issues:**

1. **File not found:** Verify path exists
2. **Unsupported format:** Check file extension
3. **OCR fails on image:** Ensure image is clear, text is readable
4. **Audio transcription empty:** Check audio quality, try different format

**Debug mode:**
```bash
markitdown problematic.pdf 2>&1 | head -20
```

## Output Characteristics

- **Clean Markdown:** Optimized for LLM token efficiency
- **Structure preserved:** Headings, lists, tables maintained
- **Metadata included:** EXIF for images, document properties for Office files
- **No temp files:** Streaming approach, memory efficient
- **UTF-8 output:** Handles international characters

## Advanced Features

**Azure Document Intelligence** (enhanced PDF processing):
```python
from markitdown import MarkItDown

md = MarkItDown(
    docintel_endpoint="https://your-resource.cognitiveservices.azure.com/",
    docintel_key="your-key"
)
result = md.convert("complex.pdf")
```

**LLM image descriptions** (GPT-4o integration):
```python
from markitdown import MarkItDown
from openai import OpenAI

client = OpenAI()
md = MarkItDown(llm_client=client, llm_model="gpt-4o")
result = md.convert("presentation.pptx")
```

**See references/advanced_integrations.md** for complete details.

## Resources

- **references/python_api.md** — Complete Python API documentation
- **references/advanced_integrations.md** — Azure DI and LLM integration
- **references/format_specifics.md** — Format-specific options and quirks
