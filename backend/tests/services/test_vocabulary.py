from unittest.mock import patch

import pytest

from models import Language, PartOfSpeech
from services.vocabulary import get_lemma, get_card

pytestmark = pytest.mark.asyncio

NOUN = PartOfSpeech.noun.value
ADJ = PartOfSpeech.adj.value
VERB = PartOfSpeech.verb.value


@pytest.mark.parametrize("word, lang, expected_lemma", [
    ("liep", Language.NL, "lopen"),
    ("went", Language.EN, "go"),
    ("идут", Language.RU, "идти")
])
def test_get_lemma(word, lang, expected_lemma):
    assert get_lemma(word, lang) == expected_lemma


def make_doc(noun_translations, adj_translations):
    # документ в том виде, в каком он лежит в базе
    return {
        "lemma": "licht",
        "lang": Language.NL.value,
        "readings": {
            NOUN: {"grammar": "het licht (meervoud: lichten)", "translations": noun_translations},
            ADJ: {"grammar": "licht (lichter, lichtst)", "translations": adj_translations},
        },
    }


async def test_get_card_exists(mock_db):
    await mock_db["vocabulary"].insert_one(make_doc(
        {Language.RU.value: "свет", Language.EN.value: "light"},
        {Language.RU.value: "лёгкий", Language.EN.value: "light, easy"},
    ))

    with patch("services.vocabulary.generate_card") as mock_generate_card:
        card = await get_card("licht", Language.NL, Language.RU)

        mock_generate_card.assert_not_called()

    assert card["lemma"] == "licht"
    assert card["lang"] == Language.NL.value
    assert card["readings"] == [
        {"pos": NOUN, "grammar": "het licht (meervoud: lichten)", "translation": "свет"},
        {"pos": ADJ, "grammar": "licht (lichter, lichtst)", "translation": "лёгкий"},
    ]


async def test_get_card_not_exists(mock_db):
    with patch("services.vocabulary.generate_card") as mock_generate_card:
        mock_generate_card.return_value = [
            {"pos": NOUN, "grammar": "het licht (meervoud: lichten)", "translation": "свет"},
            {"pos": ADJ, "grammar": "licht (lichter, lichtst)", "translation": "лёгкий"},
        ]
        card = await get_card("licht", Language.NL, Language.RU)

        mock_generate_card.assert_called_once()

    assert card["lemma"] == "licht"
    assert [r["pos"] for r in card["readings"]] == [NOUN, ADJ]
    assert card["readings"][0]["translation"] == "свет"
    assert card["readings"][1]["translation"] == "лёгкий"

    saved = await mock_db["vocabulary"].find_one({"lemma": "licht", "lang": Language.NL.value})
    assert saved["readings"][NOUN]["grammar"] == "het licht (meervoud: lichten)"
    assert saved["readings"][NOUN]["translations"][Language.RU.value] == "свет"
    assert saved["readings"][ADJ]["translations"][Language.RU.value] == "лёгкий"


async def test_get_card_without_translation(mock_db):
    # у существительного уже есть перевод на ru, у прилагательного ещё нет
    await mock_db["vocabulary"].insert_one(make_doc(
        {Language.RU.value: "свет", Language.EN.value: "light"},
        {Language.EN.value: "light, easy"},
    ))

    with patch("services.vocabulary.generate_card") as mock_generate_card:
        mock_generate_card.return_value = [
            {"pos": NOUN, "grammar": "xxx", "translation": "ЛАМПА"},  # уже переведено, не трогаем
            {"pos": ADJ, "grammar": "xxx", "translation": "лёгкий"},
            {"pos": VERB, "grammar": "xxx", "translation": "лишнее"},  # в документе такого нет
        ]
        card = await get_card("licht", Language.NL, Language.RU)

        mock_generate_card.assert_called_once()

    # грамматика из базы, а не от AI; существующий перевод не перезаписан
    assert card["readings"] == [
        {"pos": NOUN, "grammar": "het licht (meervoud: lichten)", "translation": "свет"},
        {"pos": ADJ, "grammar": "licht (lichter, lichtst)", "translation": "лёгкий"},
    ]

    saved = await mock_db["vocabulary"].find_one({"lemma": "licht", "lang": Language.NL.value})
    assert saved["readings"][NOUN]["translations"][Language.RU.value] == "свет"
    assert saved["readings"][ADJ]["translations"][Language.RU.value] == "лёгкий"
    assert saved["readings"][ADJ]["translations"][Language.EN.value] == "light, easy"
    assert VERB not in saved["readings"]


async def test_get_card_skips_reading_without_translation(mock_db):
    await mock_db["vocabulary"].insert_one(make_doc(
        {Language.EN.value: "light"},
        {Language.EN.value: "light, easy"},
    ))

    with patch("services.vocabulary.generate_card") as mock_generate_card:
        # AI на этот раз вернул только существительное
        mock_generate_card.return_value = [
            {"pos": NOUN, "grammar": "xxx", "translation": "свет"},
        ]
        card = await get_card("licht", Language.NL, Language.RU)

    assert [r["pos"] for r in card["readings"]] == [NOUN]
    assert card["readings"][0]["translation"] == "свет"


async def test_get_card_lost_race(mock_db):
    # документ уже есть (его создал другой запрос), но db_get_lemma его не увидела
    await mock_db["vocabulary"].create_index([("lemma", 1), ("lang", 1)], unique=True)
    await mock_db["vocabulary"].insert_one(make_doc(
        {Language.EN.value: "light"},
        {Language.EN.value: "light, easy"},
    ))

    with patch("services.vocabulary.db_get_lemma", return_value=None), \
            patch("services.vocabulary.generate_card") as mock_generate_card:
        mock_generate_card.return_value = [
            {"pos": NOUN, "grammar": "xxx", "translation": "свет"},
            {"pos": ADJ, "grammar": "xxx", "translation": "лёгкий"},
        ]
        card = await get_card("licht", Language.NL, Language.RU)

        # AI вызван один раз, второй раз не нужен
        mock_generate_card.assert_called_once()

    assert card["readings"][0]["translation"] == "свет"
    assert card["readings"][1]["translation"] == "лёгкий"

    count = await mock_db["vocabulary"].count_documents({"lemma": "licht", "lang": Language.NL.value})
    assert count == 1
    saved = await mock_db["vocabulary"].find_one({"lemma": "licht", "lang": Language.NL.value})
    assert saved["readings"][NOUN]["translations"][Language.EN.value] == "light"
    assert saved["readings"][NOUN]["translations"][Language.RU.value] == "свет"