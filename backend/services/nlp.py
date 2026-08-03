import spacy

from models import Language

nlp_nl = spacy.load("nl_core_news_sm")
nlp_en = spacy.load("en_core_web_sm")
nlp_ru = spacy.load("ru_core_news_sm")

nlp_models = {
    Language.NL: nlp_nl,
    Language.EN: nlp_en,
    Language.RU: nlp_ru
}