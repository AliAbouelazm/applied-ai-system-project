# 🎵 Music Recommender Simulation

## Project Summary

This project builds a small music recommender that takes a user's genre, mood, and energy preferences and scores every song in a 10-song catalog against those preferences. The system ranks songs by their total score and returns the top results. Each recommendation also comes with a short reason explaining why that song was suggested. I built two versions: a functional one using plain dictionaries and a class-based one using `Song`, `UserProfile`, and `Recommender` objects.

---

## How The System Works

- Each `Song` stores: title, artist, genre, mood, energy level (0 to 1), tempo in BPM, valence (how positive it sounds), danceability, and acousticness
- `UserProfile` stores a user's favorite genre, favorite mood, target energy level, and whether they like acoustic music
- The `Recommender` scores each song by adding points for genre and mood matches, then penalizing songs whose energy is far from the user's target. Acoustic songs get a small bonus if the user likes them, or a small penalty if they don't. Valence adds a tiny bonus on top.
- Songs get sorted from highest to lowest score and the top k are returned

Score breakdown per song:
- Genre match: +3.0
- Mood match: +2.0
- Energy distance: -2.0 times the absolute difference from the user's target
- Acousticness: +acousticness if user likes acoustic, -0.5 times acousticness otherwise
- Valence: +0.5 times valence

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

- Tried dropping the genre weight from 3.0 down to 1.0. The results got a lot more mixed since energy and mood started pulling more weight. The top pick for a pop/happy user became a lofi track just because its energy was closer. Raised it back to 3.0 because genre matching felt like the most important signal.

- Tested a user who likes acoustic music (likes_acoustic=True, genre=jazz, mood=relaxed). Without the acoustic bonus, the jazz track "Coffee Shop Stories" was getting beaten by tracks with better energy matches. Adding the acousticness bonus pushed it to the top where it belonged.

- Ran a "high energy rock fan" profile (genre=rock, mood=intense, energy=0.9). The system correctly put "Storm Runner" first with a big lead over everything else. That felt right.

- Changed the energy penalty multiplier from 2.0 to 4.0. The recommendations became too rigid and pretty much only returned songs within a very narrow energy band regardless of genre or mood. 2.0 felt like a better balance.

---

## Limitations and Risks

- The catalog only has 10 songs so the recommendations barely vary between similar users
- Lyrics, language, and cultural context are completely ignored
- The genre weight is high enough that two users with the same genre preference but totally different tastes in other ways will get nearly identical results
- Acoustic preference is a binary yes or no when in reality people want different amounts depending on their mood
- There is no way for the system to learn from what a user actually skips or replays

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Building this made me realize how much real recommenders are doing behind the scenes. What looks like a "personalized" experience is actually just a scoring function running across a catalog, and whoever designed the weights decides what matters most. If genre gets a higher weight than mood, the whole system tilts that way whether it fits the user or not. That kind of hidden bias is easy to miss because the output still looks reasonable on the surface.

The other thing I noticed is how quickly the system breaks down at scale. With 10 songs, the results feel okay. But if the catalog stayed this limited and the user population grew, every person who likes pop would get the same two or three songs over and over. Diversity and fairness would have to be built in on purpose because they definitely don't just appear on their own.
