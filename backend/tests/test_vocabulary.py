import pytest

from models import Language
from services.vocabulary import get_lemma


@pytest.mark.parametrize("word, lang, expected_lemma", [
    ("liep", Language.NL, "lopen"),
    ("went", Language.EN, "go"),
    ("идут", Language.RU, "идти")
])

def test_get_lemma(word, lang, expected_lemma):
    assert get_lemma(word, lang) == expected_lemma