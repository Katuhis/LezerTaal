from unittest.mock import patch

import pytest

from exceptions import CardNotFoundError, TranslationNotFoundError, CardAlreadyExistsError
from models import Language, PartOfSpeech
from services.vocabulary import get_lemma, get_card, create_card, add_translation

pytestmark = pytest.mark.asyncio

NOUN = PartOfSpeech.noun.value
ADJ = PartOfSpeech.adj.value
VERB = PartOfSpeech.verb.value

NOUN_GRAMMAR = "het licht (meervoud: lichten)"
ADJ_GRAMMAR = "licht (lichter, lichtst)"


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
            NOUN: {"grammar": NOUN_GRAMMAR, "translations": noun_translations},
            ADJ: {"grammar": ADJ_GRAMMAR, "translations": adj_translations},
        },
    }


async def find_saved(mock_db):
    return await mock_db["vocabulary"].find_one({"lemma": "licht", "lang": Language.NL.value})


# ---------- get_card ----------

async def test_get_card_success(mock_db):
    doc = make_doc(
        {Language.RU.value: "свет", Language.EN.value: "light"},
        {Language.RU.value: "лёгкий", Language.EN.value: "light, easy"},
    )
    await mock_db["vocabulary"].insert_one(doc)

    with patch("services.vocabulary.generate_card") as mock_generate_card:
        card = await get_card("licht", Language.NL, Language.RU)

        mock_generate_card.assert_not_called()

    assert card == {
        "lemma": "licht",
        "lang": Language.NL.value,
        "readings": [
            {"pos": NOUN, "grammar": NOUN_GRAMMAR, "translation": "свет"},
            {"pos": ADJ, "grammar": ADJ_GRAMMAR, "translation": "лёгкий"},
        ],
    }
    # в ответе нет служебных полей Mongo
    assert "_id" not in card


async def test_get_card_not_found(mock_db):
    with patch("services.vocabulary.generate_card") as mock_generate_card:
        with pytest.raises(CardNotFoundError):
            await get_card("licht", Language.NL, Language.RU)

        mock_generate_card.assert_not_called()

    assert await find_saved(mock_db) is None


async def test_get_card_translation_not_found(mock_db):
    # у существительного перевод на ru есть, у прилагательного нет
    doc = make_doc(
        {Language.RU.value: "свет", Language.EN.value: "light"},
        {Language.EN.value: "light, easy"},
    )
    await mock_db["vocabulary"].insert_one(doc)

    with patch("services.vocabulary.generate_card") as mock_generate_card:
        with pytest.raises(TranslationNotFoundError):
            await get_card("licht", Language.NL, Language.RU)

        mock_generate_card.assert_not_called()

    # get ничего не меняет в базе
    assert await find_saved(mock_db) == doc


# ---------- create_card ----------

async def test_create_card_success(mock_db):
    with patch("services.vocabulary.generate_card") as mock_generate_card:
        mock_generate_card.return_value = [
            {"pos": NOUN, "grammar": NOUN_GRAMMAR, "translation": "свет"},
            {"pos": ADJ, "grammar": ADJ_GRAMMAR, "translation": "лёгкий"},
        ]
        card = await create_card("licht", Language.NL, Language.RU)

        mock_generate_card.assert_called_once()

    assert card == {
        "lemma": "licht",
        "lang": Language.NL.value,
        "readings": [
            {"pos": NOUN, "grammar": NOUN_GRAMMAR, "translation": "свет"},
            {"pos": ADJ, "grammar": ADJ_GRAMMAR, "translation": "лёгкий"},
        ],
    }

    saved = await find_saved(mock_db)
    assert saved["readings"][NOUN]["grammar"] == NOUN_GRAMMAR
    assert saved["readings"][NOUN]["translations"] == {Language.RU.value: "свет"}
    assert saved["readings"][ADJ]["translations"] == {Language.RU.value: "лёгкий"}


async def test_create_card_already_exists(mock_db):
    doc = make_doc(
        {Language.EN.value: "light"},
        {Language.EN.value: "light, easy"},
    )
    await mock_db["vocabulary"].insert_one(doc)

    with patch("services.vocabulary.generate_card") as mock_generate_card:
        with pytest.raises(CardAlreadyExistsError):
            await create_card("licht", Language.NL, Language.RU)

        # AI не вызывается, деньги не тратим
        mock_generate_card.assert_not_called()

    assert await find_saved(mock_db) == doc


async def test_create_card_lost_race(mock_db):
    # другой запрос успел создать карточку (только с en), но наша проверка её не увидела
    await mock_db["vocabulary"].create_index([("lemma", 1), ("lang", 1)], unique=True)
    doc = make_doc(
        {Language.EN.value: "light"},
        {Language.EN.value: "light, easy"},
    )
    await mock_db["vocabulary"].insert_one(doc)

    with patch("services.vocabulary.db_get_lemma", return_value=None), \
            patch("services.vocabulary.generate_card") as mock_generate_card:
        mock_generate_card.return_value = [
            {"pos": NOUN, "grammar": "xxx", "translation": "свет"},
            {"pos": ADJ, "grammar": "xxx", "translation": "лёгкий"},
        ]
        # в базе осталась чужая карточка без перевода на ru, клиент должен вызвать add_translation
        with pytest.raises(TranslationNotFoundError):
            await create_card("licht", Language.NL, Language.RU)

        mock_generate_card.assert_called_once()

    count = await mock_db["vocabulary"].count_documents({"lemma": "licht", "lang": Language.NL.value})
    assert count == 1
    assert await find_saved(mock_db) == doc


# ---------- add_translation ----------

async def test_add_translation_success(mock_db):
    # у существительного уже есть ru, у прилагательного нет
    await mock_db["vocabulary"].insert_one(make_doc(
        {Language.RU.value: "свет", Language.EN.value: "light"},
        {Language.EN.value: "light, easy"},
    ))

    with patch("services.vocabulary.generate_card") as mock_generate_card:
        mock_generate_card.return_value = [
            {"pos": NOUN, "grammar": "xxx", "translation": "ЛАМПА"},   # уже переведено, не трогаем
            {"pos": ADJ, "grammar": "xxx", "translation": "лёгкий"},
            {"pos": VERB, "grammar": "xxx", "translation": "лишнее"},  # в документе такого нет
        ]
        card = await add_translation("licht", Language.NL, Language.RU)

        mock_generate_card.assert_called_once()

    # грамматика из базы, существующий перевод не перезаписан
    assert card["readings"] == [
        {"pos": NOUN, "grammar": NOUN_GRAMMAR, "translation": "свет"},
        {"pos": ADJ, "grammar": ADJ_GRAMMAR, "translation": "лёгкий"},
    ]

    saved = await find_saved(mock_db)
    assert saved["readings"][NOUN]["translations"][Language.RU.value] == "свет"
    assert saved["readings"][ADJ]["translations"][Language.RU.value] == "лёгкий"
    assert saved["readings"][ADJ]["translations"][Language.EN.value] == "light, easy"
    assert VERB not in saved["readings"]


async def test_add_translation_not_found(mock_db):
    with patch("services.vocabulary.generate_card") as mock_generate_card:
        with pytest.raises(CardNotFoundError):
            await add_translation("licht", Language.NL, Language.RU)

        mock_generate_card.assert_not_called()


async def test_add_translation_nothing_missing(mock_db):
    doc = make_doc(
        {Language.RU.value: "свет"},
        {Language.RU.value: "лёгкий"},
    )
    await mock_db["vocabulary"].insert_one(doc)

    with patch("services.vocabulary.generate_card") as mock_generate_card:
        card = await add_translation("licht", Language.NL, Language.RU)

        # всё уже переведено, AI не вызываем
        mock_generate_card.assert_not_called()

    assert [r["translation"] for r in card["readings"]] == ["свет", "лёгкий"]
    assert await find_saved(mock_db) == doc


async def test_add_translation_ai_skipped_reading(mock_db):
    await mock_db["vocabulary"].insert_one(make_doc(
        {Language.EN.value: "light"},
        {Language.EN.value: "light, easy"},
    ))

    with patch("services.vocabulary.generate_card") as mock_generate_card:
        # AI вернул только существительное
        mock_generate_card.return_value = [
            {"pos": NOUN, "grammar": "xxx", "translation": "свет"},
        ]
        with pytest.raises(TranslationNotFoundError):
            await add_translation("licht", Language.NL, Language.RU)

    # то, что AI вернул, записалось; прилагательное осталось без перевода на ru
    saved = await find_saved(mock_db)
    assert saved["readings"][NOUN]["translations"][Language.RU.value] == "свет"
    assert Language.RU.value not in saved["readings"][ADJ]["translations"]