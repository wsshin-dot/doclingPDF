import os
import sys
import shutil
import argparse
import asyncio
from typing import List

# --- 라이브러리 임포트 ---
try:
    from docling.document_converter import DocumentConverter
    from docling.chunking import HierarchicalChunker

    from llama_index.core import (
        VectorStoreIndex,
        StorageContext,
        load_index_from_storage,
    )
    from llama_index.core.schema import TextNode
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.core import Settings

    from mcp.server.fastmcp import FastMCP
except ImportError as e:
    print(
        f"Error: Missing required packages. Please run: pip install -r requirements_mcp.txt"
    )
    print(f"Details: {e}")
    sys.exit(1)

# --- 설정 ---
EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"  # 작고 빠른 로컬 모델
PERSIST_DIR = "./pdf_vector_store"
SERVER_NAME = "PDF-RAG-Server"

# 글로벌 설정 (임베딩 모델 초기화)
embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)
Settings.embedding_model = embed_model
Settings.llm = None  # 임베딩만 할 것이므로 LLM 불필요


def load_and_index_pdf(pdf_path: str):
    """
    1. Docling으로 PDF 로드
    2. HierarchicalChunker로 청킹 (문맥 유지)
    3. LlamaIndex 벡터 스토어 생성 및 저장
    """
    print(f"[1/4] Loading PDF with Docling: {pdf_path}")
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    doc = result.document

    print(f"[2/4] Chunking with HierarchicalChunker...")
    chunker = HierarchicalChunker()
    chunks = list(chunker.chunk(doc))
    print(f"      -> Created {len(chunks)} chunks.")

    print(f"[3/4] Creating Embeddings & Index (using {EMBED_MODEL_NAME})...")

    # Docling 청크 -> LlamaIndex 노드 변환
    nodes = []
    for chunk in chunks:
        # 메타데이터에 헤더 정보 포함 (검색 정확도 상승 핵심)
        metadata = {
            "source": os.path.basename(pdf_path),
            "headings": " > ".join(chunk.meta.headings)
            if chunk.meta.headings
            else "None",
        }

        # 텍스트와 메타데이터 결합
        node = TextNode(text=chunk.text, metadata=metadata)
        nodes.append(node)

    # 인덱스 생성 (임베딩 모델 명시적 전달)
    if os.path.exists(PERSIST_DIR):
        shutil.rmtree(PERSIST_DIR)

    index = VectorStoreIndex(nodes, embed_model=embed_model)

    # 디스크에 저장
    index.storage_context.persist(persist_dir=PERSIST_DIR)
    print(f"[4/4] Index saved to '{PERSIST_DIR}'")

    return index


def get_query_engine():
    """저장된 인덱스를 로드하여 검색 엔진 반환"""
    if not os.path.exists(PERSIST_DIR):
        raise FileNotFoundError(
            f"Index not found in {PERSIST_DIR}. Run indexing first."
        )

    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context, embed_model=embed_model)

    # 상위 5개 결과 반환
    return index.as_retriever(similarity_top_k=5)


# --- MCP 서버 설정 ---
mcp = FastMCP(SERVER_NAME)


@mcp.tool()
def query_datasheet(query: str) -> str:
    """
    Search the PDF datasheet for technical details.
    Use this to find register definitions, memory maps, timing specs, etc.
    Returns the most relevant text segments from the document.
    """
    try:
        retriever = get_query_engine()
        nodes = retriever.retrieve(query)

        response = f"Found {len(nodes)} relevant sections:\n\n"
        for i, node in enumerate(nodes):
            meta = node.metadata
            response += f"--- Result {i + 1} (Section: {meta.get('headings')}) ---\n"
            response += f"{node.get_content()}\n\n"

        return response
    except Exception as e:
        return f"Error searching datasheet: {str(e)}"


# --- 메인 실행 ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PDF to RAG MCP Server")
    parser.add_argument("pdf_path", nargs="?", help="Path to the PDF file to index")

    args = parser.parse_args()

    # PDF 경로가 주어지면 인덱싱 수행
    if args.pdf_path:
        if not os.path.exists(args.pdf_path):
            print(f"Error: File not found: {args.pdf_path}")
            sys.exit(1)

        load_and_index_pdf(args.pdf_path)
        print("\n[SUCCESS] Indexing Complete! Starting MCP Server...")
        print("   Add this server to your Cursor/OpenCode config:")
        print(f"   Command: python {os.path.abspath(__file__)}")

        # 인덱싱 후 바로 서버 시작
        mcp.run()

    # 경로 없이 실행되면 서버만 시작 (기존 인덱스 사용)
    else:
        if os.path.exists(PERSIST_DIR):
            print(f"Starting MCP Server with existing index in '{PERSIST_DIR}'...")
            mcp.run()
        else:
            print("Error: No existing index found. Please provide a PDF path first.")
            print(f"Usage: python {os.path.basename(__file__)} <path_to_pdf>")
