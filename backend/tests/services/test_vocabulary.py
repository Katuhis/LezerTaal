from unittest.mock import patch

import pytest

from models import Language, PartOfSpeech
from services.vocabulary import get_lemma, get_card

pytestmark = pytest.mark.asyncio

@pytest.mark.parametrize("word, lang, expected_lemma", [
    ("liep", Language.NL, "lopen"),
    ("went", Language.EN, "go"),
    ("идут", Language.RU, "идти")
])

def test_get_lemma(word, lang, expected_lemma):
    assert get_lemma(word, lang) == expected_lemma

async def test_get_card_exists(mock_db):
    lemma = "huis"
    lang = Language.NL

    await mock_db["vocabulary"].insert_one(
        {
            "lemma": lemma,
            "lang": lang.value,
            "pos": PartOfSpeech.noun.value,
            "grammar": "het",
            "translations": {Language.RU.value: "дом", Language.EN.value: "house"}
        })

    with patch("services.vocabulary.generate_card") as mock_generate_card:
        card = await get_card("huizen", Language.NL, Language.RU)

        mock_generate_card.assert_not_called()
        assert card["lemma"] == lemma
        assert card["pos"] == PartOfSpeech.noun.value
        assert card["grammar"] == "het"
        assert card["translation"] == "дом"

async def test_get_card_not_exists(mock_db):
    with patch("services.vocabulary.generate_card") as mock_generate_card:
        mock_generate_card.return_value = {
            "pos": PartOfSpeech.noun.value,
            "grammar": "het",
            "translation": "дом"
        }
        card = await get_card("huizen", Language.NL, Language.RU)

        assert card["lemma"] == "huis"
        assert card["pos"] == PartOfSpeech.noun.value
        assert card["grammar"] == "het"
        assert card["translation"] == "дом"
        mock_generate_card.assert_called_once()

        new_card = await mock_db["vocabulary"].find_one({"lemma": "huis", "lang": Language.NL.value})
        assert new_card["lemma"] == "huis"
        assert new_card["pos"] == PartOfSpeech.noun.value
        assert new_card["grammar"] == "het"
        assert new_card["translations"][Language.RU.value] == "дом"

async def test_get_card_without_translate(mock_db):
    lemma = "huis"
    lang = Language.NL

    await mock_db["vocabulary"].insert_one(
        {
            "lemma": lemma,
            "lang": lang.value,
            "pos": PartOfSpeech.noun.value,
            "grammar": "het",
            "translations": {Language.EN.value: "house"}
        })

    with patch("services.vocabulary.generate_card") as mock_generate_card:
        mock_generate_card.return_value = {
            "pos": PartOfSpeech.verb.value,
            "grammar": "xxx",
            "translation": "дом"
        }
        card = await get_card("huizen", Language.NL, Language.RU)
        assert card["lemma"] == "huis"
        assert card["pos"] == PartOfSpeech.noun.value
        assert card["grammar"] == "het"
        assert card["translation"] == "дом"
        mock_generate_card.assert_called_once()

        new_card = await mock_db["vocabulary"].find_one({"lemma": "huis", "lang": Language.NL.value})
        assert new_card["translations"][Language.RU.value] == "дом"
        assert new_card["translations"][Language.EN.value] == "house"