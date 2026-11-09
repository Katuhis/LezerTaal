from pymongo.errors import DuplicateKeyError

from database.database import vocabulary_collection
from models import Language


async def db_get_lemma(lemma: str, lang: Language) -> dict | None:
    result = await vocabulary_collection.find_one({'lemma': lemma, 'lang': lang.value})
    return result

async def db_create_lemma(lemma: str, lang: Language, user_lang: Language, readings: list[dict]) -> dict:
    card = {
        'lemma': lemma,
        'lang': lang.value,
        'readings': {}
    }
    for reading in readings:
        card["readings"][reading["pos"]] = {
            "grammar": reading["grammar"],
            "translations": {user_lang.value: reading["translation"]}
        }
    try:
        await vocabulary_collection.insert_one(card)
        result = card
    except DuplicateKeyError:
        result = await vocabulary_collection.find_one({'lemma': lemma, 'lang': lang.value})
    return result

async def db_add_translation(
        lemma: str,
        lang: Language,
        user_lang: Language,
        translations: dict) -> int:
    if not translations:
        return 0

    updates = {}
    for pos, translation in translations.items():
        updates[f'readings.{pos}.translations.{user_lang.value}'] = translation

    result = await vocabulary_collection.update_one(
        {'lemma': lemma, 'lang': lang.value},
        {'$set': updates}
    )
    return result.modified_count
