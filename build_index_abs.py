import os
import shutil
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.schema import TextNode
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

BASE_DIR = r"D:\workspace\doclingPDF"
PERSIST_DIR = os.path.join(BASE_DIR, "pdf_vector_store")
MD_FILE_PATH = os.path.join(BASE_DIR, "TC38X_50pages.md")
EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"

# 설정
embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)
Settings.embedding_model = embed_model
Settings.llm = None


def build_index():
    print(f"Working Directory: {os.getcwd()}")
    print(f"Target Vector Store: {PERSIST_DIR}")

    with open(MD_FILE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = content.split("\n## ")
    nodes = []
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
        text = f"## {chunk}" if i > 0 else chunk
        node = TextNode(text=text)
        nodes.append(node)

    if os.path.exists(PERSIST_DIR):
        shutil.rmtree(PERSIST_DIR)

    # 명시적 모델 전달
    index = VectorStoreIndex(nodes, embed_model=embed_model)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
    print(f"Saved index to: {PERSIST_DIR}")


if __name__ == "__main__":
    build_index()
