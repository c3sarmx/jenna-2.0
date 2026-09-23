import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


GOOGLE_TRANSLATE_URL = (
    "https://translation.googleapis.com/language/translate/v2"
)


class GoogleTranslateError(RuntimeError):
    """Raised when Google Cloud Translation cannot translate text."""


def _get_api_key():
    api_key = os.environ.get("GOOGLE_TRANSLATE_API_KEY")

    if not api_key:
        raise GoogleTranslateError(
            "GOOGLE_TRANSLATE_API_KEY environment variable is required"
        )

    return api_key


def translate_to_spanish(text, source_language=None):
    """
    Translate text to Spanish using Google Cloud Translation.

    If the source language is already Spanish, the original text is
    returned without making an API request.
    """
    if text is None:
        raise ValueError("text is required")

    text = str(text).strip()

    if not text:
        return ""

    if source_language:
        normalized_language = source_language.split("-", 1)[0].lower()

        if normalized_language == "es":
            return text

    api_key = _get_api_key()

    payload = {
        "q": text,
        "target": "es",
        "format": "text",
    }

    if source_language:
        payload["source"] = source_language

    url = f"{GOOGLE_TRANSLATE_URL}?{urlencode({'key': api_key})}"

    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=15) as response:
            response_payload = json.loads(
                response.read().decode("utf-8")
            )
    except HTTPError as exc:
        raise GoogleTranslateError(
            f"Google Translation API returned HTTP {exc.code}"
        ) from exc
    except URLError as exc:
        raise GoogleTranslateError(
            "Unable to reach Google Translation API"
        ) from exc
    except json.JSONDecodeError as exc:
        raise GoogleTranslateError(
            "Google Translation API returned invalid JSON"
        ) from exc

    translations = (
        response_payload
        .get("data", {})
        .get("translations", [])
    )

    if not translations:
        raise GoogleTranslateError(
            "Google Translation API returned no translation"
        )

    translated_text = translations[0].get("translatedText")

    if not translated_text:
        raise GoogleTranslateError(
            "Google Translation API returned an empty translation"
        )

    return translated_text
