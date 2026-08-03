from models import Language
from services.nlp import nlp_models


def get_lemma(word: str, lang: Language) -> str:
    nlp = nlp_models[lang]
    doc = nlp(word)
    return doc[0].lemma_.lower()