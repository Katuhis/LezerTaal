from models import Language
from services.nlp import nlp_models
from services.ai import generate_card
from database.vocabulary import db_get_lemma, db_create_lemma, db_add_translation


def get_lemma(word: str, lang: Language) -> str:
    nlp = nlp_models[lang]
    doc = nlp(word)
    return doc[0].lemma_.lower()

async def get_card(
        word: str,
        lang: Language,
        user_lang: Language
) -> dict:
    lemma = get_lemma(word, lang)

    card = await db_get_lemma(lemma, lang)

    if card:
        if card["translations"].get(user_lang.value):
            result = {
                "lemma": lemma,
                "lang": lang.value,
                "pos": card["pos"],
                "grammar": card["grammar"],
                "translation": card["translations"][user_lang.value]
            }
        else:
            new_card = await generate_card(lemma, lang, user_lang)
            await db_add_translation(lemma, lang, user_lang, new_card["translation"])
            result = {
                "lemma": lemma,
                "lang": lang.value,
                "pos": card["pos"],
                "grammar": card["grammar"],
                "translation": new_card["translation"]
            }
    else:
        new_card = await generate_card(lemma, lang, user_lang)
        inserted_card = await db_create_lemma(
            lemma,
            lang,
            new_card["pos"],
            new_card["grammar"],
            user_lang,
            new_card["translation"]
        )
        result = {
            "lemma": lemma,
            "lang": lang.value,
            "pos": inserted_card["pos"],
            "grammar": inserted_card["grammar"],
            "translation": new_card["translation"]
        }

    return result