import json
import anthropic

from config import ANTHROPIC_API_KEY
from services.prompts import WORD_EXPLANATION_PROMPT


def build_prompt(word, context_sentence, text_language, user_language):
    return WORD_EXPLANATION_PROMPT.format(
        word=word,
        context_sentence=context_sentence,
        text_language=text_language,
        user_language=user_language
    )

def get_explanation(word, context_sentence, text_language, user_language):
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        ready_prompt = build_prompt(
            word,
            context_sentence,
            text_language,
            user_language
        )

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            messages=[{"role": "user", "content": ready_prompt}]
        )

        raw = response.content[0].text
        clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        res = json.loads(clean)
        return res
    except anthropic.APIError as e:
        raise ValueError(f"Anthropic API error: {type(e).__name__}: {e}") from e
    except json.JSONDecodeError as e:
        raise ValueError("JSON decode error") from e
    except Exception as e:
        raise ValueError(f"Unexpected error: {type(e).__name__}: {e}") from e
