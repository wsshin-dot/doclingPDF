# Docling PDF to Markdown Converter

Python tools for converting PDF documents to Markdown using [Docling](https://github.com/docling-project/docling).

## Features

- **GPU Acceleration**: Automatic GPU detection for faster processing
- **OCR Support**: Optional OCR for scanned documents
- **Chunk Processing**: Handle large PDFs by processing in chunks
- **CLI Interface**: Easy command-line usage

## Installation

```bash
pip install docling pypdfium2
```

## Usage

### Single File Conversion

```bash
python convert_to_md.py input.pdf -o output.md
```

Options:
- `-o, --output`: Output file path (default: same name with .md extension)
- `--no-gpu`: Disable GPU acceleration
- `--no-ocr`: Disable OCR (faster for digital PDFs)

### Large PDF (Chunk Processing)

```bash
python convert_chunks.py input.pdf -o output.md -c 10
```

Options:
- `-o, --output`: Output file path
- `-c, --chunk-size`: Pages per chunk (default: 10)
- `--no-gpu`: Disable GPU acceleration
- `--no-ocr`: Disable OCR

## Performance Tips

1. **Disable OCR** for digital PDFs: `--no-ocr`
2. **Use GPU** if available (enabled by default)
3. **Adjust chunk size** based on available memory

## License

MIT
