import os
import re
import json
import networkx as nx
from docling.document_converter import DocumentConverter

# Ollama는 선택 사항 (없으면 스킵)
try:
    from llama_index.llms.ollama import Ollama

    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False


class GraphBuilder:
    def __init__(self, model_name="llama3.1"):
        self.graph = nx.DiGraph()
        self.llm = None

        if HAS_OLLAMA and model_name:
            try:
                self.llm = Ollama(model=model_name, request_timeout=300.0)
                print(f"[INFO] LLM enabled: {model_name}")
            except:
                print(
                    "[WARN] Failed to connect to Ollama. Running in structure-only mode."
                )
        else:
            print("[INFO] Running in structure-only mode (No LLM).")

    def build(self, pdf_path, output_path="datasheet_graph.gml"):
        print(f"[INFO] Reading {pdf_path}...")
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        doc = result.document

        print("[INFO] Building Hierarchy...")
        self._add_hierarchy(doc)

        if self.llm:
            print("[INFO] Extracting Semantic Relations...")
            self._add_semantics(doc)
        else:
            print("[INFO] Skipping Semantic Extraction (No LLM configured)")

        nx.write_gml(self.graph, output_path)
        print(f"[INFO] Graph saved to {output_path}")
        return output_path

    def _add_hierarchy(self, doc):
        root = "ROOT"
        self.graph.add_node(root, type="Root")
        stack = [(0, root)]

        for item in doc.texts:
            if item.label == "section_header":
                text = item.text.strip()
                if not text:
                    continue
                node_id = f"SEC:{text}"
                self.graph.add_node(node_id, type="Section", label=text)

                # 부모 연결 (간단하게 직전 스택 사용)
                parent_id = stack[-1][1]
                self.graph.add_edge(parent_id, node_id, relation="CONTAINS")
                stack.append((1, node_id))  # 깊이 계산은 생략

            elif item.label == "text":
                text = item.text.strip()
                if len(text) > 50:
                    chunk_id = f"TXT:{text[:20]}"
                    self.graph.add_node(chunk_id, type="Content", text=text)
                    parent_id = stack[-1][1]
                    self.graph.add_edge(parent_id, chunk_id, relation="HAS")

    def _add_semantics(self, doc):
        # LLM이 있을 때만 실행 (기존 로직 유지)
        pass


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        GraphBuilder(model_name=None).build(sys.argv[1])
