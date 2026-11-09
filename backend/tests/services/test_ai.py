import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import anthropic
import httpx
import pytest

from models import Language, PartOfSpeech
from services.ai import generate_card

pytestmark = pytest.mark.asyncio

NOUN = PartOfSpeech.noun.value
ADJ = PartOfSpeech.adj.value

READINGS = [
    {"pos": NOUN, "grammar": "het licht (meervoud: lichten)", "translation": "свет"},
    {"pos": ADJ, "grammar": "licht (lichter, lichtst)", "translation": "лёгкий"},
]


def ai_response(text):
    # то, что возвращает client.messages.create: response.content[0].text
    return SimpleNamespace(content=[SimpleNamespace(text=text)])


async def test_generate_card_success():
    with patch("services.ai.client.messages.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = ai_response(json.dumps({"readings": READINGS}))

        result = await generate_card("licht", Language.NL, Language.RU)

    assert result == READINGS

    # в промпт попали лемма и названия языков
    prompt = mock_create.call_args.kwargs["messages"][0]["content"]
    assert "licht" in prompt
    assert "Dutch" in prompt
    assert "Russian" in prompt


async def test_generate_card_markdown_wrapped_json():
    wrapped = "```json\n" + json.dumps({"readings": READINGS}) + "\n```"

    with patch("services.ai.client.messages.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = ai_response(wrapped)

        result = await generate_card("licht", Language.NL, Language.RU)

    assert result == READINGS


@pytest.mark.parametrize("text, error", [
    ("это не json", "JSON decode error"),
    ("[]", "not dictionary"),
    ("{}", "missing keys: readings"),
    ('{"readings": []}', "missing keys: readings"),
    ('{"readings": "text"}', "not list of dictionary"),
    ('{"readings": ["text"]}', "not list of dictionary"),
    ('{"readings": [{"grammar": "g", "translation": "t"}]}', "missing keys: pos"),
    ('{"readings": [{"pos": "noun", "translation": "t"}]}', "missing keys: grammar"),
    ('{"readings": [{"pos": "noun", "grammar": "g", "translation": ""}]}', "missing keys: translation"),
    ('{"readings": [{"pos": "preposition", "grammar": "g", "translation": "t"}]}', "not a valid PartOfSpeech"),
    ('{"readings": [{"pos": "noun", "grammar": "g", "translation": "t"},'
     ' {"pos": "noun", "grammar": "g", "translation": "t"}]}', "repeat pos"),
])
async def test_generate_card_invalid_response(text, error):
    with patch("services.ai.client.messages.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = ai_response(text)

        with pytest.raises(ValueError, match=error):
            await generate_card("licht", Language.NL, Language.RU)


async def test_generate_card_api_error():
    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")

    with patch("services.ai.client.messages.create", new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = anthropic.APIConnectionError(request=request)

        with pytest.raises(ValueError, match="Anthropic API error"):
            await generate_card("licht", Language.NL, Language.RU)


async def test_generate_card_unexpected_error():
    with patch("services.ai.client.messages.create", new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = RuntimeError("boom")

        with pytest.raises(ValueError, match="Unexpected error"):
            await generate_card("licht", Language.NL, Language.RU)