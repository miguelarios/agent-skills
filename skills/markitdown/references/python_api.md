# Python API Reference

Complete documentation for using MarkItDown programmatically in Python scripts.

## Basic Usage

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("document.pdf")
print(result.text_content)
```

## The MarkItDown Class

### Constructor Options

```python
MarkItDown(
    docintel_endpoint=None,    # Azure Document Intelligence endpoint
    docintel_key=None,          # Azure DI API key
    llm_client=None,            # OpenAI client for LLM features
    llm_model="gpt-4o",         # Model for image descriptions
    enable_plugins=False        # Enable plugin system (security)
)
```

### Methods

#### convert(source)

Convert a file or URL to Markdown.

**Parameters:**
- `source` (str): File path, URL, or file-like object

**Returns:**
- `ConvertResult` object with `text_content` attribute

**Example:**
```python
result = md.convert("report.pdf")
markdown_text = result.text_content
```

#### convert_stream(stream)

Convert from a file-like object (streaming).

```python
with open("document.pdf", "rb") as f:
    result = md.convert_stream(f)
    print(result.text_content)
```

## Document Conversion

### PDF Files

```python
# Basic PDF conversion
result = md.convert("document.pdf")

# With Azure Document Intelligence (better table extraction)
md = MarkItDown(
    docintel_endpoint="https://your-resource.cognitiveservices.azure.com/",
    docintel_key="your-api-key"
)
result = md.convert("complex.pdf")
```

### Office Documents

```python
# Word documents
result = md.convert("report.docx")

# PowerPoint presentations
result = md.convert("slides.pptx")

# Excel spreadsheets
result = md.convert("data.xlsx")
```

### Legacy Office Formats

```python
# Older Excel format
result = md.convert("spreadsheet.xls")
```

## Media Processing

### Images with OCR

```python
# JPEG, PNG, GIF, etc.
result = md.convert("photo.jpg")

# Includes EXIF metadata and OCR text
print(result.text_content)
```

### Audio Transcription

```python
# WAV, MP3, etc.
result = md.convert("recording.wav")

# Transcribed speech as Markdown
print(result.text_content)
```

**Note:** Requires `speech_recognition` package (included in `markitdown[all]`).

## Web Content

### YouTube Transcripts

```python
result = md.convert("https://youtube.com/watch?v=VIDEO_ID")
print(result.text_content)
```

### HTML Files

```python
result = md.convert("webpage.html")
```

### EPUB Books

```python
result = md.convert("book.epub")
```

## Structured Data

### CSV Files

```python
result = md.convert("data.csv")
# Output: Markdown table
```

### JSON Files

```python
result = md.convert("config.json")
# Output: Formatted Markdown
```

### XML Files

```python
result = md.convert("data.xml")
```

## Batch Processing

### ZIP Archives

```python
result = md.convert("archive.zip")
# All files converted and concatenated
```

### Directory Processing

```python
import os
from pathlib import Path

md = MarkItDown()
output_dir = Path("markdown_output")
output_dir.mkdir(exist_ok=True)

# Convert all PDFs in directory
for pdf_file in Path("documents").glob("*.pdf"):
    result = md.convert(str(pdf_file))
    output_file = output_dir / f"{pdf_file.stem}.md"
    output_file.write_text(result.text_content)
```

## Error Handling

```python
from markitdown import MarkItDown
import sys

md = MarkItDown()

try:
    result = md.convert("document.pdf")
    print(result.text_content)
except FileNotFoundError:
    print("File not found", file=sys.stderr)
except Exception as e:
    print(f"Conversion failed: {e}", file=sys.stderr)
```

## Performance Tips

1. **Streaming for large files:** Use `convert_stream()` for files >100MB
2. **Batch processing:** Process ZIP archives instead of individual files
3. **Memory efficiency:** MarkItDown uses streaming, no temp files created
4. **Azure DI:** Use for complex PDFs with tables and layouts

## Integration Examples

### RAG Pipeline

```python
from markitdown import MarkItDown

md = MarkItDown()
documents = ["manual.pdf", "guide.docx", "faq.html"]

markdown_docs = []
for doc in documents:
    result = md.convert(doc)
    markdown_docs.append(result.text_content)

# Now ready for embedding and indexing
all_content = "\n\n---\n\n".join(markdown_docs)
```

### Document Analysis

```python
from markitdown import MarkItDown

md = MarkItDown()

# Convert and analyze
result = md.convert("report.pdf")
markdown = result.text_content

# Count sections
sections = markdown.count("\n## ")

# Extract metadata
if "Date:" in markdown:
    # Process date information
    pass
```
