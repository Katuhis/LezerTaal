import json
import anthropic

from config import ANTHROPIC_API_KEY
from models import Language, PartOfSpeech
from services.prompts import CARD_PROMPT

client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

LANGUAGE_NAMES = {
    Language.NL: "Dutch",
    Language.EN: "English",
    Language.RU: "Russian",
}

async def generate_card(lemma: str, text_language: Language, user_language: Language) -> list[dict]:
    try:

        ready_prompt = CARD_PROMPT.format(
            lemma=lemma,
            text_language=LANGUAGE_NAMES[text_language],
            user_language=LANGUAGE_NAMES[user_language]
        )

        response = await client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=800,
            messages=[{"role": "user", "content": ready_prompt}]
        )

        raw = response.content[0].text
        clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        res = json.loads(clean)

    except anthropic.APIError as e:
        raise ValueError(f"Anthropic API error: {type(e).__name__}: {e}") from e
    except json.JSONDecodeError as e:
        raise ValueError("JSON decode error") from e
    except Exception as e:
        raise ValueError(f"Unexpected error: {type(e).__name__}: {e}") from e

    if not(isinstance(res, dict)):
        raise ValueError("AI response is not dictionary")
    if not(res.get("readings")):
        raise ValueError("AI response is missing keys: readings")
    if not(isinstance(res.get("readings"), list)):
        raise ValueError("AI response is not list of dictionary")
    poses = set()
    for word in res.get("readings"):
        if not (isinstance(word, dict)):
            raise ValueError("AI response is not list of dictionary")
        if word.get("pos") is None:
            raise ValueError("AI response is missing keys: pos")
        if word.get("grammar") is None:
            raise ValueError("AI response is missing keys: grammar")
        if not word.get("translation"):
            raise ValueError("AI response is missing keys: translation")
        PartOfSpeech(word["pos"])
        if word["pos"] not in poses:
            poses.add(word["pos"])
        else:
            raise ValueError("AI response repeat pos")

    return res["readings"]