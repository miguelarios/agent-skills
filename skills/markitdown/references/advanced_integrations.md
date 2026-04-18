# Advanced Integrations

Enhance MarkItDown with AI-powered features and cloud services.

## Azure Document Intelligence

Azure Document Intelligence provides enhanced PDF processing with better table extraction, layout analysis, and handwriting recognition.

### Setup

1. **Create Azure DI resource:**
   - Go to Azure Portal
   - Create "Document Intelligence" resource
   - Get endpoint and API key

2. **Install with Azure support:**
   ```bash
   uv tool install 'markitdown[all]'
   ```

### Usage

```python
from markitdown import MarkItDown

md = MarkItDown(
    docintel_endpoint="https://your-resource.cognitiveservices.azure.com/",
    docintel_key="your-api-key"
)

result = md.convert("complex-document.pdf")
print(result.text_content)
```

### When to Use Azure DI

**Use Azure DI for:**
- Complex tables with merged cells
- Multi-column layouts
- Handwritten text
- Poor quality scans
- Forms with checkboxes

**Use standard PDF for:**
- Simple text documents
- Single-column layouts
- Clean, digital PDFs
- Cost-sensitive applications

### Cost Considerations

- **Standard PDF:** Free, local processing
- **Azure DI:** Pay per page (check Azure pricing)
- **Recommendation:** Start with standard, upgrade if quality insufficient

## LLM-Powered Image Descriptions

Generate detailed, contextual descriptions of images using GPT-4o.

### Setup

1. **Install OpenAI SDK:**
   ```bash
   uv pip install openai
   ```

2. **Set API key:**
   ```bash
   export OPENAI_API_KEY="your-key"
   ```

### Usage

```python
from markitdown import MarkItDown
from openai import OpenAI

client = OpenAI()
md = MarkItDown(llm_client=client, llm_model="gpt-4o")

# Images in presentations get detailed descriptions
result = md.convert("presentation.pptx")
print(result.text_content)
```

### How It Works

1. MarkItDown extracts images from documents (PPTX, DOCX, etc.)
2. Sends images to GPT-4o Vision API
3. Generates contextual descriptions
4. Embeds descriptions in Markdown output

### Use Cases

- **Presentations:** Describe charts, diagrams, screenshots
- **Documents:** Explain figures, photos, illustrations
- **Spreadsheets:** Describe embedded charts

### Cost Considerations

- **GPT-4o Vision:** ~$0.005 per image (check OpenAI pricing)
- **Recommendation:** Use selectively for important images only

## Custom Plugins

MarkItDown supports extensible plugins for custom conversion logic.

### Security Note

Plugins are **disabled by default** for security. Only enable if you trust the plugin source.

### Enabling Plugins

```python
from markitdown import MarkItDown

md = MarkItDown(enable_plugins=True)
result = md.convert("custom-file.xyz")
```

### Plugin Development

Create custom converters for proprietary or specialized formats:

```python
from markitdown import MarkItDown, Converter

class CustomConverter(Converter):
    def convert(self, stream):
        # Custom conversion logic
        return "# Custom Format\n\nContent..."

# Register plugin (requires plugin system setup)
# See MarkItDown plugin documentation
```

### Plugin Use Cases

- Proprietary file formats
- Domain-specific document types
- Custom preprocessing pipelines
- Integration with internal tools

## Performance Optimization

### Batch Processing

```python
from markitdown import MarkItDown
from concurrent.futures import ThreadPoolExecutor

md = MarkItDown()

def convert_file(filepath):
    result = md.convert(filepath)
    return filepath, result.text_content

# Process 10 files in parallel
with ThreadPoolExecutor(max_workers=10) as executor:
    files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
    results = list(executor.map(convert_file, files))
```

### Memory Management

For very large files (>500MB):

```python
from markitdown import MarkItDown

md = MarkItDown()

# Use streaming for large files
with open("large-document.pdf", "rb") as f:
    result = md.convert_stream(f)
    # Process in chunks if needed
    print(result.text_content[:10000])  # First 10k chars
```

### Caching

```python
import hashlib
from pathlib import Path
from markitdown import MarkItDown

md = MarkItDown()
cache_dir = Path("markdown_cache")
cache_dir.mkdir(exist_ok=True)

def cached_convert(filepath):
    # Create cache key from file hash
    file_hash = hashlib.md5(Path(filepath).read_bytes()).hexdigest()
    cache_file = cache_dir / f"{file_hash}.md"

    if cache_file.exists():
        return cache_file.read_text()

    result = md.convert(filepath)
    cache_file.write_text(result.text_content)
    return result.text_content
```

## Integration Patterns

### RAG System Integration

```python
from markitdown import MarkItDown
import chromadb

md = MarkItDown()
client = chromadb.Client()
collection = client.create_collection("documents")

# Convert and index documents
for i, filepath in enumerate(["doc1.pdf", "doc2.pdf"]):
    result = md.convert(filepath)
    collection.add(
        documents=[result.text_content],
        metadatas=[{"source": filepath}],
        ids=[f"doc_{i}"]
    )
```

### API Service

```python
from fastapi import FastAPI, UploadFile
from markitdown import MarkItDown
import tempfile

app = FastAPI()
md = MarkItDown()

@app.post("/convert")
async def convert_document(file: UploadFile):
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Convert to Markdown
    result = md.convert(tmp_path)
    return {"markdown": result.text_content}
```

### Background Job Queue

```python
from markitdown import MarkItDown
from rq import Queue
from redis import Redis

md = MarkItDown()
redis_conn = Redis()
q = Queue(connection=redis_conn)

def convert_document(filepath, output_path):
    result = md.convert(filepath)
    Path(output_path).write_text(result.text_content)
    return output_path

# Queue conversion job
job = q.enqueue(convert_document, "report.pdf", "report.md")
```
