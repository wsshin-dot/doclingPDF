import os
import sys
import shutil
import argparse
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.schema import TextNode
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings

# --- 설정 ---
EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"
PERSIST_DIR = "./pdf_vector_store"
MD_FILE_PATH = r"D:\workspace\doclingPDF\TC38X_50pages.md"

# 글로벌 설정
embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)
Settings.embedding_model = embed_model
Settings.llm = None


def load_and_index_md():
    print(f"[1/3] Reading Markdown file: {MD_FILE_PATH}")

    if not os.path.exists(MD_FILE_PATH):
        print("Error: Markdown file not found.")
        return

    with open(MD_FILE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"[2/3] Chunking by headers...")
    chunks = content.split("\n## ")

    nodes = []
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue

        text = f"## {chunk}" if i > 0 else chunk
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


if __name__ == "__main__":
    load_and_index_md()
