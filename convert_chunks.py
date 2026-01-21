"""
Docling PDF Chunk Converter
Process large PDFs in chunks for better memory management and progress tracking
Optimized with GPU acceleration support
"""

import os
import argparse
import time
from pathlib import Path
import pypdfium2 as pdfium
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
    
    accelerator_options = AcceleratorOptions(
        device=AcceleratorDevice.AUTO if use_gpu else AcceleratorDevice.CPU,
        num_threads=4,
    )
    
    pipeline_options = PdfPipelineOptions(
        accelerator_options=accelerator_options,
        do_ocr=not disable_ocr,
        generate_page_images=False,
        generate_picture_images=False,
    )
    
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options
            )
        }
    )
    
    return converter


def convert_pdf_in_chunks(
    source: str,
    output: str = None,
    chunk_size: int = 10,
    use_gpu: bool = True,
    disable_ocr: bool = False,
):
    """Convert a large PDF file to Markdown in chunks."""
    
    source_path = Path(source)
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source}")
    
    if output is None:
        output = source_path.with_suffix(".md")
    
    print(f"Converting: {source}")
    print(f"Chunk size: {chunk_size} pages")
    print(f"GPU: {'enabled (auto)' if use_gpu else 'disabled'}")
    print(f"OCR: {'disabled' if disable_ocr else 'enabled'}")
    
    # Initialize output file
    with open(output, "w", encoding="utf-8") as f:
        f.write("")
    
    # Load PDF and get page count
    pdf = pdfium.PdfDocument(source)
    total_pages = len(pdf)
    print(f"Total pages: {total_pages}")
    
    converter = create_optimized_converter(use_gpu=use_gpu, disable_ocr=disable_ocr)
    
    start_time = time.time()
    
    for i in range(0, total_pages, chunk_size):
        chunk_start = i
        chunk_end = min(i + chunk_size, total_pages)
        progress = (chunk_start / total_pages) * 100
        
        print(f"Processing pages {chunk_start + 1}-{chunk_end} ({progress:.1f}%)...")
        
        # Extract chunk to temporary PDF
        new_pdf = pdfium.PdfDocument.new()
        page_indices = list(range(chunk_start, chunk_end))
        new_pdf.import_pages(pdf, page_indices)
        
        temp_pdf_path = f"_temp_chunk_{i}.pdf"
        new_pdf.save(temp_pdf_path)
        
        try:
            result = converter.convert(temp_pdf_path)
            markdown = result.document.export_to_markdown()
            
            with open(output, "a", encoding="utf-8") as f:
                f.write(f"\n\n<!-- Pages {chunk_start + 1}-{chunk_end} -->\n\n")
                f.write(markdown)
            
        except Exception as e:
            print(f"Error on pages {chunk_start + 1}-{chunk_end}: {e}")
        finally:
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)
    
    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.2f}s ({elapsed/total_pages:.2f}s/page) -> {output}")
    
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Convert large PDF to Markdown in chunks using Docling"
    )
    parser.add_argument("source", help="Path to the PDF file")
    parser.add_argument("-o", "--output", help="Output Markdown file path")
    parser.add_argument(
        "-c", "--chunk-size", type=int, default=10,
        help="Number of pages per chunk (default: 10)"
    )
    parser.add_argument(
        "--no-gpu", action="store_true", help="Disable GPU acceleration"
    )
    parser.add_argument(
        "--no-ocr", action="store_true", help="Disable OCR (faster for digital PDFs)"
    )
    
    args = parser.parse_args()
    
    convert_pdf_in_chunks(
        source=args.source,
        output=args.output,
        chunk_size=args.chunk_size,
        use_gpu=not args.no_gpu,
        disable_ocr=args.no_ocr,
    )


if __name__ == "__main__":
    main()
