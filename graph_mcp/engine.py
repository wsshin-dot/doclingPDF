import os
import networkx as nx


class GraphEngine:
    def __init__(self, graph_path="datasheet_graph.gml"):
        self.graph_path = graph_path
        self.graph = None
        self._load_graph()

    def _load_graph(self):
        if os.path.exists(self.graph_path):
            self.graph = nx.read_gml(self.graph_path)
            print(f"[INFO] Loaded graph: {self.graph_path}")
        else:
            print(f"[WARN] Graph file not found: {self.graph_path}")

    def query(self, question):
        """
        질문에 관련된 그래프 노드를 찾아서 '텍스트 맥락(Context)'만 반환합니다.
        LLM(Gemini)이 이 맥락을 보고 최종 답변을 만듭니다.
        """
        if not self.graph:
            return "Error: Graph not loaded. Please build the graph first."

        # 1. 키워드 검색으로 시작 노드 찾기
        start_nodes = self._find_nodes(question)
        if not start_nodes:
            return "No related entities found in the graph."

        # 2. 맥락 추출 (Context Retrieval)
        context = self._get_context(start_nodes)
        return context

    def _find_nodes(self, question):
        # 1. 노드 이름 매칭
        nodes = []
        q_upper = question.upper()

        for node in self.graph.nodes():
            node_str = str(node).upper()

            # 노드 이름에서 검색
            if q_upper in node_str:
                nodes.append(node)
                continue

            # 노드 내용(text 속성)에서 검색
            node_data = self.graph.nodes[node]
            if "text" in node_data:
                if q_upper in node_data["text"].upper():
                    nodes.append(node)

        return nodes[:10]  # 최대 10개

    def _get_context(self, nodes):
        lines = []
        lines.append("=== Graph RAG Context ===")

        for node in nodes:
            if node in self.graph:
                # 노드 자체 정보
                node_data = self.graph.nodes[node]
                lines.append(f"\n[Entity: {node}]")
                if "text" in node_data:
                    lines.append(f"Content: {node_data['text'][:200]}...")

                # 연결된 관계 (1-hop)
                for nbr in self.graph.neighbors(node):
                    edge = self.graph.get_edge_data(node, nbr)
                    rel = edge.get("relation", "related")
                    lines.append(f"  --[{rel}]--> {nbr}")

        return "\n".join(lines)
