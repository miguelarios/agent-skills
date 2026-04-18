# Format-Specific Details

Detailed information about how different file formats are handled.

## PDF Files

### Standard PDF Processing

- **Engine:** pdfminer.six (local, no external dependencies)
- **Output:** Preserves text structure, headings, paragraphs
- **Tables:** Basic table detection (use Azure DI for complex tables)
- **Images:** Extracted separately, not embedded in output

### Limitations

- Scanned PDFs require OCR (not included in standard processing)
- Complex layouts may lose structure
- Tables with merged cells may not render perfectly

### Best Practices

```bash
# For clean, digital PDFs
markitdown digital-doc.pdf -o output.md

# For complex PDFs, use Azure DI
# (requires setup in Python API)
```

## Office Documents

### Word (DOCX)

- **Preserves:** Headings, lists, tables, hyperlinks
- **Images:** Extracted with OCR (if text present)
- **Styles:** Converted to Markdown equivalents
- **Track changes:** Not supported

```bash
markitdown report.docx -o report.md
```

### PowerPoint (PPTX)

- **Slides:** Converted to sections (## Slide 1, ## Slide 2)
- **Text:** Bullet points, titles preserved
- **Images:** Extracted and described (use LLM for detailed descriptions)
- **Notes:** Speaker notes included

```bash
markitdown presentation.pptx -o slides.md
```

### Excel (XLSX, XLS)

- **Sheets:** Each sheet becomes a section
- **Tables:** Converted to Markdown tables
- **Formatting:** Basic formatting preserved
- **Charts:** Not extracted (images only)

```bash
markitdown spreadsheet.xlsx -o data.md
```

### Legacy Office (XLS)

- **Support:** Limited compared to XLSX
- **Recommendation:** Convert to XLSX first if possible

## Images

### Supported Formats

- JPEG, PNG, GIF, BMP, TIFF
- WebP, SVG (limited)

### OCR Processing

- **Engine:** Tesseract (via pytesseract)
- **Accuracy:** Depends on image quality
- **Languages:** English by default (configurable)

### EXIF Metadata

- Camera make/model
- Date/time captured
- GPS coordinates (if available)
- Orientation

```bash
markitdown photo.jpg -o photo.md
```

### Tips for Better OCR

- Use high-resolution images (300+ DPI)
- Ensure good contrast
- Straighten rotated text
- Remove backgrounds if possible

## Audio Files

### Supported Formats

- WAV, MP3, M4A, FLAC
- OGG, WebM

### Transcription

- **Engine:** speech_recognition library
- **Accuracy:** Depends on audio quality
- **Languages:** English by default
- **Speaker separation:** Not supported (mono output)

```bash
markitdown meeting.wav -o transcript.md
```

### Limitations

- No speaker diarization (can't distinguish speakers)
- Background noise affects accuracy
- Long files may take time to process

### Tips for Better Transcription

- Use high-quality audio (minimal background noise)
- Clear speech, normal pace
- WAV format preferred over compressed formats

## Web Content

### HTML Files

- **Structure:** Preserves headings, lists, tables
- **Links:** Maintained as Markdown links
- **Images:** Alt text extracted, images not downloaded
- **Scripts:** Ignored

```bash
markitdown webpage.html -o page.md
```

### YouTube Videos

- **Transcript:** Extracts auto-generated or manual captions
- **Languages:** Supports multiple languages
- **Format:** Clean text with timestamps removed

```bash
markitdown "https://youtube.com/watch?v=VIDEO_ID" -o transcript.md
```

### Limitations

- Requires internet connection
- Videos without captions return empty
- Live streams not supported

### EPUB Books

- **Chapters:** Converted to sections
- **Formatting:** Preserved as Markdown
- **Images:** Extracted if present

```bash
markitdown book.epub -o book.md
```

## Structured Data

### CSV Files

- **Output:** Markdown table
- **Headers:** First row used as column names
- **Encoding:** UTF-8 assumed

```bash
markitdown data.csv -o data.md
```

### JSON Files

- **Output:** Formatted Markdown with structure preserved
- **Arrays:** Converted to lists
- **Objects:** Converted to key-value pairs

```bash
markitdown config.json -o config.md
```

### XML Files

- **Output:** Hierarchical Markdown structure
- **Attributes:** Preserved where possible
- **Namespaces:** Stripped

```bash
markitdown data.xml -o data.md
```

## Archives

### ZIP Files

- **Processing:** Extracts and converts all supported files
- **Output:** Concatenated Markdown from all files
- **Order:** Alphabetical by filename

```bash
markitdown archive.zip -o all-docs.md
```

### Limitations

- Large archives may take time
- Nested archives (ZIP within ZIP) not supported
- Password-protected archives not supported

## Format Detection

MarkItDown uses file extensions to detect format. If extension is missing or wrong:

```bash
# Force specific format (not directly supported)
# Rename file with correct extension
mv document.xyz document.pdf
markitdown document.pdf
```

## Common Issues

### Encoding Problems

```bash
# If you get encoding errors, try:
file document.pdf  # Check file type
dos2unix document.txt  # Fix line endings
```

### Corrupted Files

```bash
# Test if file is valid
pdfinfo document.pdf  # For PDFs
file document.docx    # Check file type
```

### Large Files

```bash
# For files >500MB, use streaming (Python API)
# Or split into smaller chunks
```

## Performance by Format

**Fast (<1s for typical files):**
- CSV, JSON, XML
- HTML, Markdown
- Small images

**Medium (1-5s):**
- DOCX, XLSX, PPTX
- PDF (simple)
- Audio clips (<1 min)

**Slow (>5s):**
- PDF (complex, many pages)
- Large images (OCR)
- Long audio files
- ZIP archives with many files
