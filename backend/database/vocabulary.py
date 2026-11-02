from pymongo.errors import DuplicateKeyError

from database.database import vocabulary_collection
from models import Language


async def db_get_lemma(lemma: str, lang: Language) -> dict | None:
    result = await vocabulary_collection.find_one({'lemma': lemma, 'lang': lang.value})
    return result

async def db_create_lemma(lemma: str, lang: Language, pos: str, grammar: str, user_lang: Language, translation: str) -> dict:
    card = {
        'lemma': lemma,
        'lang': lang.value,
        'pos': pos,
        'grammar': grammar,
        'translations': {
            user_lang.value: translation
        }
    }
    try:
        await vocabulary_collection.insert_one(card)
        result = card
    except DuplicateKeyError:
        result = await vocabulary_collection.find_one({'lemma': lemma, 'lang': lang.value})
    return result

async def db_add_translation(lemma: str, lang: Language, user_lang: Language, translation: str) -> int:
    result = await vocabulary_collection.update_one(
        {'lemma': lemma, 'lang': lang.value},
        {'$set': {f'translations.{user_lang.value}': translation}}
    )
    return result.modified_count
