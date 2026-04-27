"""
Evaluation harness for VibeFinder.

Runs a fixed set of test cases through the full RAG pipeline and reports
how accurately Claude parses preferences and whether the retriever surfaces
the expected top song. Run with:

    python eval.py
"""

import os
import sys
import logging

from dotenv import load_dotenv

from src.logger import setup_logging
from src.rag import RAGPipeline

load_dotenv()
setup_logging()
logging.disable(logging.CRITICAL)  # suppress noise during eval output

# Each case defines an input query and what we expect the pipeline to produce.
TEST_CASES = [
    {
        "query": "something upbeat and happy for a morning run",
        "expect_genre": "pop",
        "expect_mood": "happy",
        "expect_top_song": "Sunrise City",
    },
    {
        "query": "chill lofi for studying late at night",
        "expect_genre": "lofi",
        "expect_mood": "chill",
        "expect_top_song": None,  # any chill lofi song is acceptable
    },
    {
        "query": "heavy intense rock for the gym",
        "expect_genre": "rock",
        "expect_mood": "intense",
        "expect_top_song": "Storm Runner",
    },
    {
        "query": "acoustic jazz on a slow Sunday morning",
        "expect_genre": "jazz",
        "expect_mood": "relaxed",
        "expect_top_song": "Coffee Shop Stories",
    },
    {
        "query": "something moody and electronic for a night drive",
        "expect_genre": "synthwave",
        "expect_mood": "moody",
        "expect_top_song": "Night Drive Loop",
    },
]

SEP = "=" * 60


def run_eval() -> None:
    pipeline = RAGPipeline()
    passed = 0
    total = len(TEST_CASES)

    print(f"\n{SEP}")
    print("VibeFinder — Evaluation Harness")
    print(SEP)

    for i, case in enumerate(TEST_CASES, 1):
        print(f"\nTest {i}: {case['query']!r}")
        try:
            result = pipeline.run(case["query"], k=3)
            prefs = result["parsed_prefs"]
            top_song = result["songs"][0][0]["title"] if result["songs"] else None

            genre_ok = prefs["genre"] == case["expect_genre"]
            mood_ok = prefs["mood"] == case["expect_mood"]
            top_ok = (case["expect_top_song"] is None) or (
                top_song == case["expect_top_song"]
            )
            test_passed = genre_ok and mood_ok and top_ok
            passed += int(test_passed)

            status = "PASS" if test_passed else "FAIL"
            print(f"  [{status}]")
            print(
                f"  genre  : {prefs['genre']:12s} (expected {case['expect_genre']:12s}) {'ok' if genre_ok else 'MISMATCH'}"
            )
            print(
                f"  mood   : {prefs['mood']:12s} (expected {case['expect_mood']:12s}) {'ok' if mood_ok else 'MISMATCH'}"
            )
            if case["expect_top_song"]:
                top_display = top_song or "none"
                print(
                    f"  top    : {top_display:25s} (expected {case['expect_top_song']:25s}) {'ok' if top_ok else 'MISMATCH'}"
                )

        except Exception as exc:
            print(f"  [ERROR] {exc}")

    print(f"\n{SEP}")
    print(f"Results: {passed}/{total} passed  ({passed / total * 100:.0f}%)")
    print(SEP)


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set. Add it to a .env file.")
        sys.exit(1)
    run_eval()
