from models import Language
from services.nlp import nlp_models
from services.ai import generate_card
from database.vocabulary import db_get_lemma, db_create_lemma, db_add_translation


def get_lemma(word: str, lang: Language) -> str:
    nlp = nlp_models[lang]
    doc = nlp(word)
    return doc[0].lemma_.lower()

async def get_card(word: str, lang: Language, user_lang: Language) -> dict:
    lemma = get_lemma(word, lang)
    user_key = user_lang.value

    card = await db_get_lemma(lemma, lang)
    ai_readings = None

    # 1. Карточки нет: просим AI и создаём
    if not card:
        ai_readings = await generate_card(lemma, lang, user_lang)
        card = await db_create_lemma(lemma, lang, user_lang, ai_readings)

    # 2. Какие прочтения ещё без перевода на язык пользователя
    missing = [
        pos for pos, reading in card["readings"].items()
        if user_key not in reading["translations"]
    ]
    if missing:
        if ai_readings is None:
            ai_readings = await generate_card(lemma, lang, user_lang)
        new_translations = {
            r["pos"]: r["translation"]
            for r in ai_readings
            if r["pos"] in missing
        }
        await db_add_translation(lemma, lang, user_lang, new_translations)
        for pos, translation in new_translations.items():
            card["readings"][pos]["translations"][user_key] = translation

    # 3. Собираем ответ
    readings = [
        {
            "pos": pos,
            "grammar": reading["grammar"],
            "translation": reading["translations"][user_key],
        }
        for pos, reading in card["readings"].items()
        if user_key in reading["translations"]
    ]
    return {"lemma": lemma, "lang": lang.value, "readings": readings}