import pytest

from database.vocabulary import db_get_lemma, db_create_lemma, db_add_translation
from models import Language, PartOfSpeech

pytestmark = pytest.mark.asyncio

async def test_get_lemma_success(mock_db):
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

    result = await db_get_lemma(lemma, lang)
    assert result["lemma"] == lemma

async def test_get_lemma_failure(mock_db):
    result = await db_get_lemma("bestaatniet", Language.NL)

    assert result is None

async def test_create_lemma_success(mock_db):
    lemma = "huis"
    lang = Language.NL
    grammar = "het"
    translation = "house"

    result = await db_create_lemma(
        lemma, lang, PartOfSpeech.noun.value, grammar, Language.EN, translation
    )

    saved = await mock_db["vocabulary"].find_one({"_id": result["_id"]})
    assert saved is not None
    assert saved["lemma"] == lemma
    assert saved["lang"] == Language.NL.value
    assert saved["pos"] == PartOfSpeech.noun.value
    assert saved["grammar"] == grammar
    assert saved["translations"][Language.EN.value] == translation

async def test_create_lemma_duplicate(mock_db):
    await mock_db["vocabulary"].create_index([("lemma", 1), ("lang", 1)], unique=True)

    lemma = "huis"
    lang = Language.NL
    grammar = "het"
    translation1 = "house"

    await db_create_lemma(
        lemma, lang, PartOfSpeech.noun.value, grammar, Language.EN, translation1
    )

    translation2 = "home"

    result_second = await db_create_lemma(
        lemma, lang, PartOfSpeech.noun.value, grammar, Language.EN, translation2
    )

    assert result_second["translations"][Language.EN.value] == translation1

    count = await mock_db["vocabulary"].count_documents({"lemma": lemma, "lang": Language.NL.value})
    assert count == 1

async def test_add_translation_success(mock_db):
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
    result = await db_add_translation(lemma, lang, Language.RU, "дом")
    assert result == 1

    card = await mock_db["vocabulary"].find_one({"lemma": lemma, "lang": lang.value})
    assert card["translations"][Language.EN.value] == "house"
    assert card["translations"][Language.RU.value] == "дом"

async def test_add_translation_failure(mock_db):
    result = await db_add_translation("huis", Language.NL,  Language.RU, "дом")
    assert result == 0

