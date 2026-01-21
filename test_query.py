import os
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# 설정
BASE_DIR = r"D:\workspace\doclingPDF"
PERSIST_DIR = os.path.join(BASE_DIR, "pdf_vector_store")
EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"

# 임베딩 모델 설정
embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)
Settings.embedding_model = embed_model
Settings.llm = None


def query_rag(question):
    print(f"Querying: {question}")

    if not os.path.exists(PERSIST_DIR):
        print("Error: Vector store not found.")
        return

    # 인덱스 로드
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context, embed_model=embed_model)

    # 검색 엔진 생성
    retriever = index.as_retriever(similarity_top_k=3)
    nodes = retriever.retrieve(question)

    print(f"\nFound {len(nodes)} relevant contexts:\n")
    for i, node in enumerate(nodes):
        print(
            f"--- [Context {i + 1}] (Source: {node.metadata.get('headings', 'Unknown')}) ---"
        )
        print(node.get_content())
        print("-" * 30)


if __name__ == "__main__":
    query_rag("GTM 모듈의 TOM 채널 설정법을 알려줘")
