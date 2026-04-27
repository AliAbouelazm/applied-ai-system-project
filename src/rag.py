import logging
from typing import Dict, List, Tuple

from src.recommender import load_songs, recommend_songs
from src.llm import parse_preferences, generate_recommendation

logger = logging.getLogger(__name__)

MAX_QUERY_LENGTH = 500


class RAGPipeline:
    """
    Three-step pipeline: parse natural language → retrieve matching songs → generate response.

    The retriever is the existing rule-based scoring algorithm from Module 3.
    Claude handles both the parsing step (query → structured prefs) and the
    generation step (retrieved songs → conversational recommendation).
    """

    def __init__(self, songs_path: str = "data/songs.csv"):
        self.songs = load_songs(songs_path)
        logger.info("Catalog loaded: %d songs from %s", len(self.songs), songs_path)

    def run(self, query: str, k: int = 5) -> Dict:
        """
        Run the full RAG pipeline on a free-text query.

        Returns a dict with keys:
            query        — original user input
            parsed_prefs — structured preferences extracted by Claude
            songs        — list of (song_dict, score, explanation) tuples
            response     — Claude's conversational recommendation text
        """
        # --- Guardrails ---
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")
        if len(query) > MAX_QUERY_LENGTH:
            raise ValueError(
                f"Query is too long ({len(query)} chars). Keep it under {MAX_QUERY_LENGTH}."
            )

        logger.info("RAG pipeline started for query: %r", query)

        # Step 1: Parse
        user_prefs = parse_preferences(query)

        # Step 2: Retrieve
        retrieved: List[Tuple] = recommend_songs(user_prefs, self.songs, k=k)
        logger.info(
            "Retrieved top %d songs: %s",
            len(retrieved),
            [s[0]["title"] for s in retrieved],
        )

        # Step 3: Generate
        response = generate_recommendation(query, user_prefs, retrieved)

        return {
            "query": query,
            "parsed_prefs": user_prefs,
            "songs": retrieved,
            "response": response,
        }
