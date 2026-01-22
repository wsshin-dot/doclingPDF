import unittest
import os
import shutil
from unittest.mock import MagicMock, patch
from graph_mcp.builder import GraphBuilder
from graph_mcp.engine import GraphEngine


class TestGraphRAG(unittest.TestCase):
    def setUp(self):
        # 테스트용 디렉토리 설정
        self.test_dir = "test_output"
        os.makedirs(self.test_dir, exist_ok=True)
        self.graph_path = os.path.join(self.test_dir, "test_graph.gml")

    def tearDown(self):
        # 테스트 후 정리
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch("graph_mcp.builder.DocumentConverter")
    def test_build_and_query(self, MockConverter):
        print("\n[Test] 1. Graph Building...")

        # 1. Docling 결과 Mocking
        mock_doc = MagicMock()

        # 가짜 문서 구조 생성 (섹션 -> 텍스트)
        # Section: GTM Module
        #   - Text: The GTM module controls the timer.
        # Section: ADC Module
        #   - Text: The ADC module converts analog signals.

        item1 = MagicMock()
        item1.label = "section_header"
        item1.text = "GTM Module"

        item2 = MagicMock()
        item2.label = "text"
        item2.text = "The Generic Timer Module (GTM) ensures precise timing. It triggers the ADC."

        item3 = MagicMock()
        item3.label = "section_header"
        item3.text = "ADC Module"

        item4 = MagicMock()
        item4.label = "text"
        item4.text = "The Analog-Digital Converter (ADC) receives triggers from GTM."

        mock_doc.document.texts = [item1, item2, item3, item4]

        # Mock Converter가 변환 결과를 리턴하도록 설정
        mock_result = MagicMock()
        mock_result.document = mock_doc.document
        MockConverter.return_value.convert.return_value = mock_result

        # 빌더 실행 (LLM 없이)
        builder = GraphBuilder(model_name=None)
        output_path = builder.build("fake.pdf", self.graph_path)

        # 검증: 파일 생성 여부
        self.assertTrue(os.path.exists(output_path))
        print(f"[SUCCESS] Graph file created at {output_path}")

        # 2. Query Engine 테스트
        print("\n[Test] 2. Graph Querying...")
        engine = GraphEngine(self.graph_path)

        # 질문: "GTM"
        context = engine.query("GTM")
        print(f"Context Result:\n{context}")

        # 검증: 컨텍스트에 GTM 관련 텍스트가 포함되어야 함
        self.assertIn("GTM", context)
        self.assertIn("Generic Timer Module", context)
        print("[SUCCESS] Context retrieval successful")


if __name__ == "__main__":
    unittest.main()
