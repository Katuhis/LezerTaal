import pytest

from database.vocabulary import db_get_lemma, db_create_lemma, db_add_translation
from models import Language, PartOfSpeech

pytestmark = pytest.mark.asyncio

NOUN = PartOfSpeech.noun.value
ADJ = PartOfSpeech.adj.value

# то, что возвращает generate_card
AI_READINGS = [
    {"pos": NOUN, "grammar": "het licht (meervoud: lichten)", "translation": "light"},
    {"pos": ADJ, "grammar": "licht (lichter, lichtst)", "translation": "light, easy"},
]


def make_doc(lemma, lang):
    # документ в том виде, в каком он лежит в базе
    return {
        "lemma": lemma,
        "lang": lang.value,
        "readings": {
            NOUN: {
                "grammar": "het licht (meervoud: lichten)",
                "translations": {Language.EN.value: "light"},
            },
            ADJ: {
                "grammar": "licht (lichter, lichtst)",
                "translations": {Language.EN.value: "light, easy"},
            },
        },
    }


async def test_get_lemma_success(mock_db):
    lemma = "licht"
    lang = Language.NL

    await mock_db["vocabulary"].insert_one(make_doc(lemma, lang))

    result = await db_get_lemma(lemma, lang)
    assert result["lemma"] == lemma
    assert result["readings"][NOUN]["grammar"] == "het licht (meervoud: lichten)"
    assert result["readings"][ADJ]["translations"][Language.EN.value] == "light, easy"


async def test_get_lemma_failure(mock_db):
    result = await db_get_lemma("bestaatniet", Language.NL)

    assert result is None


async def test_create_lemma_success(mock_db):
    lemma = "licht"
    lang = Language.NL

    result = await db_create_lemma(lemma, lang, Language.EN, AI_READINGS)

    saved = await mock_db["vocabulary"].find_one({"_id": result["_id"]})
    assert saved is not None
    assert saved["lemma"] == lemma
    assert saved["lang"] == lang.value
    assert set(saved["readings"]) == {NOUN, ADJ}
    assert saved["readings"][NOUN]["grammar"] == "het licht (meervoud: lichten)"
    assert saved["readings"][NOUN]["translations"] == {Language.EN.value: "light"}
    assert saved["readings"][ADJ]["grammar"] == "licht (lichter, lichtst)"
    assert saved["readings"][ADJ]["translations"] == {Language.EN.value: "light, easy"}


async def test_create_lemma_duplicate(mock_db):
    await mock_db["vocabulary"].create_index([("lemma", 1), ("lang", 1)], unique=True)

    lemma = "licht"
    lang = Language.NL

    await db_create_lemma(lemma, lang, Language.EN, AI_READINGS)

    other_readings = [
        {"pos": NOUN, "grammar": "het licht", "translation": "lamp"},
    ]
    result_second = await db_create_lemma(lemma, lang, Language.EN, other_readings)

    # вернулся уже существующий документ, а не новый
    assert result_second["readings"][NOUN]["translations"][Language.EN.value] == "light"
    assert ADJ in result_second["readings"]

    count = await mock_db["vocabulary"].count_documents({"lemma": lemma, "lang": lang.value})
    assert count == 1


async def test_add_translation_success(mock_db):
    lemma = "licht"
    lang = Language.NL

    await mock_db["vocabulary"].insert_one(make_doc(lemma, lang))

    result = await db_add_translation(
        lemma, lang, Language.RU, {NOUN: "свет", ADJ: "лёгкий"}
    )
    assert result == 1

    card = await mock_db["vocabulary"].find_one({"lemma": lemma, "lang": lang.value})
    # новые переводы добавились
    assert card["readings"][NOUN]["translations"][Language.RU.value] == "свет"
    assert card["readings"][ADJ]["translations"][Language.RU.value] == "лёгкий"
    # старые переводы и грамматика не затёрлись
    assert card["readings"][NOUN]["translations"][Language.EN.value] == "light"
    assert card["readings"][ADJ]["translations"][Language.EN.value] == "light, easy"
    assert card["readings"][NOUN]["grammar"] == "het licht (meervoud: lichten)"


async def test_add_translation_not_found(mock_db):
    result = await db_add_translation("licht", Language.NL, Language.RU, {NOUN: "свет"})
    assert result == 0


async def test_add_translation_empty(mock_db):
    await mock_db["vocabulary"].insert_one(make_doc("licht", Language.NL))

    result = await db_add_translation("licht", Language.NL, Language.RU, {})
    assert result == 0

    card = await mock_db["vocabulary"].find_one({"lemma": "licht", "lang": Language.NL.value})
    assert Language.RU.value not in card["readings"][NOUN]["translations"]