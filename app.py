import os
import logging

import streamlit as st
from dotenv import load_dotenv

from src.logger import setup_logging
from src.rag import RAGPipeline

load_dotenv()
setup_logging()

logger = logging.getLogger(__name__)

st.set_page_config(page_title="VibeFinder", page_icon="🎵", layout="centered")


@st.cache_resource
def load_pipeline() -> RAGPipeline:
    return RAGPipeline()


def render_song_card(song: dict, score: float, explanation: str) -> None:
    with st.expander(f"{song['title']} — {song['artist']}"):
        col1, col2, col3 = st.columns(3)
        col1.metric("Genre", song["genre"])
        col2.metric("Mood", song["mood"])
        col3.metric("Energy", f"{song['energy']:.2f}")
        st.write(f"**Why it matched:** {explanation}")
        st.caption(f"Relevance score: {score:.2f}")


# ── UI ──────────────────────────────────────────────────────────────────────

st.title("VibeFinder")
st.write(
    "Describe what you want to listen to in plain English. "
    "The system will figure out your preferences and pull matching songs from the catalog."
)

query = st.text_input(
    "What are you in the mood for?",
    placeholder="e.g. something chill for late night studying",
)

if st.button("Find songs", type="primary"):
    if not query.strip():
        st.warning("Type something first.")
    elif not os.environ.get("ANTHROPIC_API_KEY"):
        st.error("ANTHROPIC_API_KEY is missing. Add it to a .env file in the project root.")
    else:
        with st.spinner("Searching catalog…"):
            try:
                pipeline = load_pipeline()
                result = pipeline.run(query)
                logger.info("Query completed: %r", query)

                st.subheader("Here's what fits")
                st.write(result["response"])

                st.subheader("Matched songs")
                for song, score, explanation in result["songs"]:
                    render_song_card(song, score, explanation)

                with st.expander("Detected preferences"):
                    prefs = result["parsed_prefs"]
                    st.json(prefs)

            except ValueError as exc:
                st.error(str(exc))
                logger.warning("Validation error: %s", exc)
            except EnvironmentError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"Something went wrong — check the logs for details.")
                logger.exception("Unhandled error for query %r: %s", query, exc)
