# tests/unit/test_processors.py
import pytest
from typing import Dict, Any
from processors import (
    InputProcessor,
    ContentProcessor,
    FormatProcessor,
    OutputProcessor
)
from core.exceptions import ProcessingError


class TestInputProcessor:
    def test_process_text_input(self):
        processor = InputProcessor()
        result = processor.process_input("hello world", "text")
        
        assert result.content == "hello world"
        assert result.validation_result['valid']

    def test_validate_empty_input(self):
        processor = InputProcessor()
        with pytest.raises(ProcessingError):
            processor.process_input("", "text")

    def test_process_json_input(self):
        processor = InputProcessor()
        data = {'key': 'value'}
        result = processor.process_input(data, "json")
        
        assert result.content == data
        assert result.validation_result['valid']

    def test_invalid_input_type(self):
        processor = InputProcessor()
        with pytest.raises(ProcessingError):
            processor.process_input("data", "invalid_type")


class TestContentProcessor:
    def test_process_text_content(self):
        processor = ContentProcessor()
        result = processor.process_content(
            "Hello World",
            "text",
            {"lowercase": True}
        )
        
        assert result.processed == "hello world"

    def test_process_code_content(self):
        processor = ContentProcessor()
        code = "def test():\n  return True"
        result = processor.process_content(
            code,
            "code",
            {"format": True}
        )
        
        assert "def test():" in result.processed
        assert "return True" in result.processed

    def test_invalid_content_type(self):
        processor = ContentProcessor()
        with pytest.raises(ProcessingError):
            processor.process_content("content", "invalid_type")


class TestFormatProcessor:
    def test_format_text(self):
        processor = FormatProcessor()
        result = processor.format_content(
            "hello world",
            "text",
            {"wrap": True, "width": 5}
        )
        
        assert len(result.content.split('\n')) > 1

    def test_format_code(self):
        processor = FormatProcessor()
        result = processor.format_content(
            "print('hello')",
            "code",
            {"language": "python"}
        )
        
        assert "```python" in result.content
        assert "```" in result.content

    def test_invalid_format_type(self):
        processor = FormatProcessor()
        with pytest.raises(ProcessingError):
            processor.format_content("content", "invalid_type")


class TestOutputProcessor:
    def test_output_processing(self):
        processor = OutputProcessor()
        # Test text output
        text_result = processor.process_output(
            "Hello world",
            "text",
            {"format": "plain"}
        )
        assert text_result.content == "Hello world"
        assert text_result.validation['valid']

        # Test JSON output
        json_result = processor.process_output(
            {"message": "Hello"},
            "json"
        )
        assert json_result.content
        assert json_result.validation['valid']

        # Test invalid output
        with pytest.raises(ProcessingError):
            processor.process_output(None, "text")