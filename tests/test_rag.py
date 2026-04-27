from unittest.mock import patch
import pytest
from src.rag import RAGPipeline


@pytest.fixture
def pipeline():
    return RAGPipeline()


def test_empty_query_raises(pipeline):
    with pytest.raises(ValueError, match="empty"):
        pipeline.run("")


def test_whitespace_query_raises(pipeline):
    with pytest.raises(ValueError, match="empty"):
        pipeline.run("   ")


def test_too_long_query_raises(pipeline):
    with pytest.raises(ValueError, match="too long"):
        pipeline.run("x" * 501)


@patch("src.rag.generate_recommendation", return_value="Here are some great picks.")
@patch(
    "src.rag.parse_preferences",
    return_value={
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False,
    },
)
def test_pipeline_returns_expected_keys(mock_parse, mock_gen, pipeline):
    result = pipeline.run("upbeat pop music")
    assert set(result.keys()) == {"query", "parsed_prefs", "songs", "response"}


@patch("src.rag.generate_recommendation", return_value="Something chill for you.")
@patch(
    "src.rag.parse_preferences",
    return_value={
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.4,
        "likes_acoustic": True,
    },
)
def test_pipeline_retrieves_songs(mock_parse, mock_gen, pipeline):
    result = pipeline.run("late night lofi")
    assert len(result["songs"]) > 0
    # Each item is (song_dict, score, explanation)
    song, score, explanation = result["songs"][0]
    assert isinstance(song, dict)
    assert isinstance(score, float)
    assert isinstance(explanation, str)


@patch("src.rag.generate_recommendation", return_value="Top pop pick.")
@patch(
    "src.rag.parse_preferences",
    return_value={
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False,
    },
)
def test_retriever_respects_k(mock_parse, mock_gen, pipeline):
    result = pipeline.run("happy pop", k=3)
    assert len(result["songs"]) == 3


@patch("src.rag.generate_recommendation", return_value="Moody synthwave for you.")
@patch(
    "src.rag.parse_preferences",
    return_value={
        "genre": "synthwave",
        "mood": "moody",
        "energy": 0.75,
        "likes_acoustic": False,
    },
)
def test_synthwave_query_returns_night_drive(mock_parse, mock_gen, pipeline):
    result = pipeline.run("something moody and electronic", k=5)
    titles = [s[0]["title"] for s in result["songs"]]
    assert "Night Drive Loop" in titles
