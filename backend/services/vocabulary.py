from models import Language
from services.nlp import nlp_models
from services.ai import generate_card
from database.vocabulary import db_get_lemma, db_create_lemma, db_add_translation
from exceptions import CardNotFoundError, TranslationNotFoundError, CardAlreadyExistsError


def get_lemma(word: str, lang: Language) -> str:
    nlp = nlp_models[lang]
    doc = nlp(word)
    return doc[0].lemma_.lower()


def find_missing(card: dict, user_lang: Language) -> list[str]:
    # части речи, у которых ещё нет перевода на язык пользователя
    return [
        pos for pos, reading in card["readings"].items()
        if user_lang.value not in reading["translations"]
    ]


def build_response(card: dict, user_lang: Language) -> dict:
    # плоский ответ для пользователя; если какое-то прочтение не переведено, карточку не отдаём
    if find_missing(card, user_lang):
        raise TranslationNotFoundError

    return {
        "lemma": card["lemma"],
        "lang": card["lang"],
        "readings": [
            {
                "pos": pos,
                "grammar": reading["grammar"],
                "translation": reading["translations"][user_lang.value],
            }
            for pos, reading in card["readings"].items()
        ],
    }


async def get_card(word: str, lang: Language, user_lang: Language) -> dict:
    # только чтение, в базу ничего не пишет
    lemma = get_lemma(word, lang)

    card = await db_get_lemma(lemma, lang)
    if not card:
        raise CardNotFoundError

    return build_response(card, user_lang)


async def create_card(word: str, lang: Language, user_lang: Language) -> dict:
    lemma = get_lemma(word, lang)

    if await db_get_lemma(lemma, lang):
        raise CardAlreadyExistsError

    ai_readings = await generate_card(lemma, lang, user_lang)
    card = await db_create_lemma(lemma, lang, user_lang, ai_readings)

    return build_response(card, user_lang)


async def add_translation(word: str, lang: Language, user_lang: Language) -> dict:
    lemma = get_lemma(word, lang)

    card = await db_get_lemma(lemma, lang)
    if not card:
        raise CardNotFoundError

    missing = find_missing(card, user_lang)
    if missing:
        ai_readings = await generate_card(lemma, lang, user_lang)
        new_translations = {
            r["pos"]: r["translation"]
            for r in ai_readings
            if r["pos"] in missing
        }
        await db_add_translation(lemma, lang, user_lang, new_translations)
        for pos, translation in new_translations.items():
            card["readings"][pos]["translations"][user_lang.value] = translation

    return build_response(card, user_lang)