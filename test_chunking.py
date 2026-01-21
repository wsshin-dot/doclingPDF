from docling.document_converter import DocumentConverter
from docling.chunking import HierarchicalChunker

# Convert the dummy file to get a DoclingDocument object
converter = DocumentConverter()
result = converter.convert(r"D:\workspace\doclingPDF\dummy.md")
doc = result.document

# Initialize the chunker
chunker = HierarchicalChunker()

# Generate chunks
chunks = list(chunker.chunk(doc))

# Print results
print(f"Total chunks: {len(chunks)}")
for i, chunk in enumerate(chunks):
    print(f"--- Chunk {i} ---")
    print(f"Text: {chunk.text!r}")
    # Inspect metadata to see if it has headers/context
    print(f"Meta: {chunk.meta}")
