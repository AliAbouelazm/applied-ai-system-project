from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

@dataclass
class Song:
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> float:
        score = 0.0
        if song.genre == user.favorite_genre:
            score += 3.0
        if song.mood == user.favorite_mood:
            score += 2.0
        score -= 2.0 * abs(song.energy - user.target_energy)
        if user.likes_acoustic:
            score += song.acousticness
        else:
            score -= song.acousticness * 0.5
        score += song.valence * 0.5
        return score

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored = sorted(self.songs, key=lambda s: self._score(user, s), reverse=True)
        return scored[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append(f"genre matches your preference ({song.genre})")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood matches ({song.mood})")
        if abs(song.energy - user.target_energy) < 0.15:
            reasons.append("energy level is close to what you like")
        if user.likes_acoustic and song.acousticness > 0.6:
            reasons.append("has an acoustic feel you tend to enjoy")
        if not reasons:
            reasons.append("it fits your overall vibe")
        return "Recommended because: " + ", ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    score = 0.0
    reasons = []

    if song["genre"] == user_prefs.get("genre", ""):
        score += 3.0
        reasons.append(f"genre match ({song['genre']})")

    if song["mood"] == user_prefs.get("mood", ""):
        score += 2.0
        reasons.append(f"mood match ({song['mood']})")

    target_energy = user_prefs.get("energy", 0.5)
    energy_diff = abs(song["energy"] - target_energy)
    score -= 2.0 * energy_diff
    if energy_diff < 0.15:
        reasons.append("close energy match")

    likes_acoustic = user_prefs.get("likes_acoustic", False)
    if likes_acoustic:
        score += song["acousticness"]
        if song["acousticness"] > 0.6:
            reasons.append("acoustic feel")
    else:
        score -= song["acousticness"] * 0.5

    score += song.get("valence", 0.5) * 0.5

    if not reasons:
        reasons.append("fits your overall vibe")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons)
        scored.append((song, score, explanation))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
