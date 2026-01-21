import os
import sys
import shutil
import argparse
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.schema import TextNode
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from mcp.server.fastmcp import FastMCP

# --- 설정 ---
EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"
PERSIST_DIR = "./pdf_vector_store"
SERVER_NAME = "PDF-RAG-Server"
MD_FILE_PATH = r"D:\workspace\doclingPDF\TC38X_50pages.md"

# 글로벌 설정
embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)
Settings.embedding_model = embed_model
Settings.llm = None


def load_and_index_md():
    print(f"[1/3] Reading Markdown file: {MD_FILE_PATH}")

    if not os.path.exists(MD_FILE_PATH):
        print("Error: Markdown file not found. Please convert PDF first.")
        return

    with open(MD_FILE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 간단한 청킹: 헤더(##) 기준으로 자르기
    # Docling이 이미 잘 만들어줬으므로 헤더 기준으로 나누면 문맥이 유지됩니다.
    print(f"[2/3] Chunking by headers...")
    chunks = content.split("\n## ")

    nodes = []
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue

        # 헤더 복구
        text = f"## {chunk}" if i > 0 else chunk

        # 첫 줄을 제목으로 추출
        lines = text.split("\n")
        title = lines[0].strip().replace("#", "").strip()

        node = TextNode(
            text=text, metadata={"source": "TC38X_50pages.md", "headings": title}
        )
        nodes.append(node)

    print(f"      -> Created {len(nodes)} chunks.")
    print(f"[3/3] Creating Index with {EMBED_MODEL_NAME}...")

    if os.path.exists(PERSIST_DIR):
        try:
            shutil.rmtree(PERSIST_DIR)
        except:
            pass

    index = VectorStoreIndex(nodes, embed_model=embed_model)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
    print(f"[SUCCESS] Index saved to '{PERSIST_DIR}'")

    return index


# --- MCP 서버 ---
mcp = FastMCP(SERVER_NAME)


def get_query_engine():
    if not os.path.exists(PERSIST_DIR):
        load_and_index_md()  # 없으면 바로 생성

    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context, embed_model=embed_model)
    return index.as_retriever(similarity_top_k=5)


@mcp.tool()
def query_datasheet(query: str) -> str:
    """Search technical specs in the datasheet."""
    try:
        retriever = get_query_engine()
        nodes = retriever.retrieve(query)
        res = ""
        for n in nodes:
            res += f"--- {n.metadata.get('headings')} ---\n{n.get_content()}\n\n"
        return res
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    # 바로 인덱싱 후 서버 시작
    if not os.path.exists(PERSIST_DIR):
        load_and_index_md()

    print(f"Starting MCP Server...")
    mcp.run()
