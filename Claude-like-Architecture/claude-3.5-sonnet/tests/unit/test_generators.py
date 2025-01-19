# tests/unit/test_generators.py
import pytest
from datetime import datetime
from uuid import UUID
from generators.response.builder import ResponseBuilder, ResponseConfig
from generators.response.formatter import ResponseFormatter
from generators.artifacts.code import CodeGenerator, CodeGenerationConfig
from generators.artifacts.markdown import MarkdownGenerator, MarkdownGenerationConfig
from generators.artifacts.special import SpecialArtifactGenerator, SpecialGenerationConfig
from models.artifacts import ArtifactType
from core.exceptions import GenerationError

class TestResponseBuilder:
    @pytest.fixture
    def response_builder(self) -> ResponseBuilder:
        config = ResponseConfig(response_type="text")
        return ResponseBuilder(config)

    def test_build_text_response(self, response_builder: ResponseBuilder):
        """Test building text response."""
        response = response_builder.build_response(
            content="Hello world",
            response_type="text",
            metadata={"test": True}
        )
        assert response.content == "Hello world"
        assert response.type == "text"
        assert response.metadata.custom_data["test"] is True

    def test_build_code_response(self, response_builder: ResponseBuilder):
        """Test building code response."""
        code = "def test(): return True"
        response = response_builder.build_response(
            content=code,
            response_type="code",
            metadata={"language": "python"}
        )
        assert "def test()" in response.content
        assert response.type == "code"
        assert "python" in str(response.metadata.custom_data)

class TestCodeGenerator:
    @pytest.fixture
    def code_generator(self) -> CodeGenerator:
        config = CodeGenerationConfig(
            language="python",
            include_comments=True,
            include_docstrings=True
        )
        return CodeGenerator(config)

    def test_generate_python_code(self, code_generator: CodeGenerator):
        """Test Python code generation."""
        code_artifact = code_generator.generate_code_artifact(
            content="def greet(name): return f'Hello {name}'",
            identifier="greeting-function",
            title="Greeting Function"
        )
        assert code_artifact.type == ArtifactType.CODE
        assert "def greet" in code_artifact.content
        assert code_artifact.metadata.language == "python"

    def test_code_validation(self, code_generator: CodeGenerator):
        """Test code validation."""
        with pytest.raises(GenerationError):
            code_generator.generate_code_artifact(
                content="invalid python code :",
                identifier="invalid-code",
                title="Invalid Code"
            )