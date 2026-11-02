import json
from unittest.mock import patch, MagicMock

import anthropic
import pytest

from services.ai import get_explanation

def test_get_explanation_success():
    with patch('services.ai.anthropic.Anthropic') as mock_client:
        mock_response = MagicMock()
        mock_response.content[
            0].text = '{"headword": "hello", "grammar": "noun", "translation": "привет", "example": "Hello world", "example_translation": "Привет мир"}'
        mock_client.return_value.messages.create.return_value = mock_response

        result = get_explanation("hello", "Hello world", "English", "Russian")

        assert result["headword"] == "hello"
        assert result["translation"] == "привет"


def test_get_explanation_api_error():
    with patch('services.ai.anthropic.Anthropic') as mock_client:
        mock_client.return_value.messages.create.side_effect = anthropic.APIError(
            message="Anthropic API error",
            request=None,
            body=None
        )

        with pytest.raises(ValueError, match="Anthropic API error"):
            get_explanation("hello", "Hello world", "English", "Russian")


def test_get_explanation_invalid_json():
    with patch('services.ai.anthropic.Anthropic') as mock_client:
        mock_response = MagicMock()
        mock_response.content[0].text = "это не json"
        mock_client.return_value.messages.create.return_value = mock_response

        with pytest.raises(ValueError, match="JSON decode error"):
            get_explanation("hello", "Hello world", "English", "Russian")