from typing import Dict

from models import Language
from services.nlp import nlp_models
from database.vocabulary import db_get_lemma


def get_lemma(word: str, lang: Language) -> str:
    nlp = nlp_models[lang]
    doc = nlp(word)
    return doc[0].lemma_.lower()

async def get_card(
        lemma: str,
        lang: Language,
        user_lang: Language
) -> dict | None:
    result = {}

    card = db_get_lemma(lemma, lang)
    if card is not None:
        translation = card['translations'].get(user_lang)
        if translation is not None:
            result = Dict()