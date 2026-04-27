import os
import json
import logging
from typing import Dict, List, Tuple
import anthropic

logger = logging.getLogger(__name__)

VALID_GENRES = {"pop", "lofi", "rock", "ambient", "jazz", "synthwave", "indie pop"}
VALID_MOODS = {"happy", "chill", "intense", "relaxed", "focused", "moody"}

# Cached system prompt — sent once per session to save tokens
_SYSTEM_PROMPT = (
    "You are a music preference assistant. "
    "The catalog contains songs in these genres: pop, lofi, rock, ambient, jazz, synthwave, indie pop. "
    "Available moods: happy, chill, intense, relaxed, focused, moody. "
    "Energy is a float from 0.0 (very calm) to 1.0 (very intense)."
)


def _get_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is not set. Add it to your .env file."
        )
    return anthropic.Anthropic(api_key=api_key)


def parse_preferences(query: str) -> Dict:
    """Ask Claude to extract structured music preferences from a free-text query."""
    client = _get_client()
    logger.info("Calling Claude to parse preferences for query: %r", query)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        system=_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    "Extract music preferences from the query below. "
                    "Return ONLY a JSON object with these exact keys:\n"
                    '  "genre"        — one of: pop, lofi, rock, ambient, jazz, synthwave, indie pop\n'
                    '  "mood"         — one of: happy, chill, intense, relaxed, focused, moody\n'
                    '  "energy"       — float 0.0 to 1.0\n'
                    '  "likes_acoustic" — true or false\n\n'
                    f'Query: "{query}"\n\n'
                    "Return only the JSON, no explanation or markdown."
                ),
            }
        ],
    )

    raw = response.content[0].text.strip()
    # Strip accidental markdown fences
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1].lstrip("json").strip() if len(parts) > 1 else raw

    try:
        prefs = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse Claude JSON response: %r — %s", raw, exc)
        # Fall back to safe defaults so the pipeline keeps running
        prefs = {}

    # Validate and apply defaults
    if prefs.get("genre") not in VALID_GENRES:
        logger.warning("Invalid genre %r, defaulting to 'pop'", prefs.get("genre"))
        prefs["genre"] = "pop"
    if prefs.get("mood") not in VALID_MOODS:
        logger.warning("Invalid mood %r, defaulting to 'chill'", prefs.get("mood"))
        prefs["mood"] = "chill"
    prefs["energy"] = max(0.0, min(1.0, float(prefs.get("energy", 0.5))))
    prefs["likes_acoustic"] = bool(prefs.get("likes_acoustic", False))

    logger.info("Parsed preferences: %s", prefs)
    return prefs


def generate_recommendation(
    query: str, prefs: Dict, retrieved: List[Tuple]
) -> str:
    """Use retrieved songs as context and ask Claude to write a conversational recommendation."""
    client = _get_client()

    songs_block = "\n".join(
        f"- {song['title']} by {song['artist']} "
        f"({song['genre']}, {song['mood']}, energy {song['energy']:.2f}) — {explanation}"
        for song, _score, explanation in retrieved
    )

    logger.info("Calling Claude to generate recommendation from %d songs", len(retrieved))

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f'A user asked: "{query}"\n\n'
                    f"Their detected preferences — genre: {prefs['genre']}, "
                    f"mood: {prefs['mood']}, energy: {prefs['energy']:.1f}, "
                    f"acoustic: {prefs['likes_acoustic']}\n\n"
                    "The retriever found these songs from the catalog:\n"
                    f"{songs_block}\n\n"
                    "Write a short, conversational recommendation (3-5 sentences) "
                    "explaining why these specific songs fit what they asked for. "
                    "Reference song titles and artists by name. "
                    "Write it like a friend recommending music — no bullet points."
                ),
            }
        ],
    )

    text = response.content[0].text.strip()
    logger.info("Generated recommendation (%d chars)", len(text))
    return text
