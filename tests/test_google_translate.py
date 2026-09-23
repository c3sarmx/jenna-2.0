import json

import pytest

from app.services.google_translate import (
    GoogleTranslateError,
    translate_to_spanish,
)


def test_translate_to_spanish_returns_original_for_spanish(
    monkeypatch,
):
    def fail_urlopen(*args, **kwargs):
        raise AssertionError(
            "No debe llamar a Google para texto ya escrito en español"
        )

    monkeypatch.setattr(
        "app.services.google_translate.urlopen",
        fail_urlopen,
    )

    result = translate_to_spanish(
        "Excelente atención.",
        source_language="es",
    )

    assert result == "Excelente atención."


def test_translate_to_spanish_requires_text():
    with pytest.raises(ValueError, match="text is required"):
        translate_to_spanish(None)


def test_translate_to_spanish_returns_empty_for_empty_text():
    assert translate_to_spanish("") == ""


def test_translate_to_spanish_requires_api_key(monkeypatch):
    monkeypatch.delenv(
        "GOOGLE_TRANSLATE_API_KEY",
        raising=False,
    )

    with pytest.raises(
        GoogleTranslateError,
        match="GOOGLE_TRANSLATE_API_KEY",
    ):
        translate_to_spanish(
            "Excellent service.",
            source_language="en",
        )


def test_translate_to_spanish_uses_google_api(monkeypatch):
    monkeypatch.setenv(
        "GOOGLE_TRANSLATE_API_KEY",
        "test-api-key",
    )

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps(
                {
                    "data": {
                        "translations": [
                            {
                                "translatedText": (
                                    "Excelente servicio."
                                )
                            }
                        ]
                    }
                }
            ).encode("utf-8")

    captured = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(
        "app.services.google_translate.urlopen",
        fake_urlopen,
    )

    result = translate_to_spanish(
        "Excellent service.",
        source_language="en",
    )

    assert result == "Excelente servicio."
    assert captured["timeout"] == 15
    assert "translation.googleapis.com" in captured[
        "request"
    ].full_url
