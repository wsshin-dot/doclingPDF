from mcp.server.fastmcp import FastMCP
from builder import GraphBuilder
from engine import GraphEngine
import os

mcp = FastMCP("GraphRAG-MCP")
engine = None


@mcp.tool()
def build_datasheet_graph(pdf_path: str) -> str:
    """
    Builds a Knowledge Graph from a Datasheet PDF.
    This process extracts structure and relationships.
    """
    if not os.path.exists(pdf_path):
        return f"Error: File not found at {pdf_path}"

    try:
        # LLM 없이 구조(Hierarchy)만 빠르게 추출하는 모드로 변경 권장
        # (Ollama가 없으면 Semantic Extraction은 스킵됨)
        builder = GraphBuilder(model_name=None)
        output = builder.build(pdf_path)
        return f"Graph built successfully! Saved to {output}"
    except Exception as e:
        return f"Build failed: {str(e)}"


@mcp.tool()
def get_datasheet_context(question: str) -> str:
    """
    Retrieves relevant technical context from the Datasheet Graph.
    Returns raw data chunks and relationships.
    OpenCode should use this context to answer the user's question.
    """
    global engine
    if engine is None:
        if os.path.exists("datasheet_graph.gml"):
            engine = GraphEngine("datasheet_graph.gml")
        else:
            return "Graph not found. Run 'build_datasheet_graph' first."

    # LLM 없이 그래프 검색 결과만 반환
    return engine.query(question)


if __name__ == "__main__":
    mcp.run()
