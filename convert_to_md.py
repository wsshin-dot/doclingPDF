"""
Docling PDF to Markdown Converter
Optimized for speed with GPU acceleration and batch processing
"""

import os
import argparse
import time
from pathlib import Path
from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    AcceleratorDevice,
    AcceleratorOptions,
)
from docling.datamodel.base_models import InputFormat
from docling.document_converter import PdfFormatOption


def create_optimized_converter(use_gpu: bool = True, disable_ocr: bool = False):
    """Create an optimized DocumentConverter with performance settings."""
    
    # Configure accelerator (GPU if available)
    accelerator_options = AcceleratorOptions(
        device=AcceleratorDevice.AUTO if use_gpu else AcceleratorDevice.CPU,
        num_threads=4,
    )
    
    # Configure pipeline options
    pipeline_options = PdfPipelineOptions(
        accelerator_options=accelerator_options,
        do_ocr=not disable_ocr,
        generate_page_images=False,  # Disable to save time
        generate_picture_images=False,  # Disable to save time
    )
    
    # Create converter with optimized settings
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options
            )
        }
    )
    
    return converter


def convert_pdf_to_markdown(
    source: str,
    output: str = None,
    use_gpu: bool = True,
    disable_ocr: bool = False,
):
    """Convert a PDF file to Markdown format."""
    
    source_path = Path(source)
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source}")
    
    # Default output path
    if output is None:
        output = source_path.with_suffix(".md")
    
    print(f"Converting: {source}")
    print(f"GPU: {'enabled (auto)' if use_gpu else 'disabled'}")
    print(f"OCR: {'disabled' if disable_ocr else 'enabled'}")
    
    start_time = time.time()
    
    converter = create_optimized_converter(use_gpu=use_gpu, disable_ocr=disable_ocr)
    result = converter.convert(source)
    
    markdown_content = result.document.export_to_markdown()
    
    with open(output, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.2f}s -> {output}")
    
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF to Markdown using Docling"
    )
    parser.add_argument("source", help="Path to the PDF file")
    parser.add_argument("-o", "--output", help="Output Markdown file path")
    parser.add_argument(
        "--no-gpu", action="store_true", help="Disable GPU acceleration"
    )
    parser.add_argument(
        "--no-ocr", action="store_true", help="Disable OCR (faster for digital PDFs)"
    )
    
    args = parser.parse_args()
    
    convert_pdf_to_markdown(
        source=args.source,
        output=args.output,
        use_gpu=not args.no_gpu,
        disable_ocr=args.no_ocr,
    )


if __name__ == "__main__":
    main()
