"""
Thin wrapper around the Gemini API (Google AI Studio).

Uses only the Python standard library (urllib) so NO new pip package
needs to be installed — nothing to add to requirements.txt.

Configuration — set these as environment variables before running app.py:

    GEMINI_API_KEY   (required)  Get one at https://aistudio.google.com/apikey
    GEMINI_MODEL     (optional)  Defaults to "gemini-flash-latest"

IMPORTANT: Gemini 1.5 models (gemini-1.5-flash, gemini-1.5-pro) have been
retired by Google and no longer work, regardless of API key. Your existing
key still works fine — keys aren't tied to a model version — it just needs
to be pointed at a current model. "gemini-flash-latest" is an alias Google
keeps pointing at their newest Flash model, so this file won't need
updating again as models rotate. Override with GEMINI_MODEL if you want a
specific pinned version instead.
"""
import json
import os
import urllib.request
import urllib.error

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

SYSTEM_INSTRUCTION = (
    "You are the AI assistant embedded in the SIH26034 Packaged Commodity "
    "Compliance tool, used by Legal Metrology inspectors in India. Help "
    "users understand compliance results, the Legal Metrology (Packaged "
    "Commodities) Rules, 2011, and how to use this application. Keep "
    "answers concise and practical. If asked something unrelated to "
    "packaged-commodity compliance or this app, still answer briefly and "
    "helpfully."
)


class GeminiError(Exception):
    pass


def ask_gemini(message: str, history: list | None = None) -> str:
    if not GEMINI_API_KEY:
        raise GeminiError(
            "GEMINI_API_KEY is not set. Add it as an environment variable "
            "before starting the backend (see GEMINI_SETUP.md)."
        )

    contents = []
    for turn in (history or []):
        role = "model" if turn.get("role") == "assistant" else "user"
        text = str(turn.get("text", "")).strip()
        if text:
            contents.append({"role": role, "parts": [{"text": text}]})
    contents.append({"role": "user", "parts": [{"text": message}]})

    payload = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1024},
    }

    url = GEMINI_ENDPOINT.format(model=GEMINI_MODEL) + f"?key={GEMINI_API_KEY}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise GeminiError(f"Gemini API returned {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise GeminiError(f"Could not reach Gemini API: {e.reason}") from e

    try:
        return body["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise GeminiError("Gemini API returned an unexpected response shape.")
