# Model Card: VibeFinder

## 1. Model Name

**VibeFinder 2.0** — RAG-powered music recommender

---

## 2. Intended Use

VibeFinder is a classroom project that demonstrates how a retrieval-augmented generation pipeline can be layered on top of a simpler rule-based system. It is intended for educational use only. The catalog has 10 songs and is not meant to serve real users or run in production.

---

## 3. How the System Works

**Stage 1 — Parse:** The user's free-text query is sent to Claude (claude-sonnet-4-6). Claude returns a structured JSON object containing `genre`, `mood`, `energy` (0.0–1.0), and `likes_acoustic` (boolean).

**Stage 2 — Retrieve:** The parsed preferences are passed to the original rule-based scoring function from Module 3. Every song in the catalog receives a score based on genre match (+3.0), mood match (+2.0), energy distance (−2.0 × |difference|), acousticness bonus/penalty, and a small valence bonus. Songs are ranked by score and the top-k are returned.

**Stage 3 — Generate:** The retrieved songs are passed back to Claude alongside the original query. Claude writes a short, conversational recommendation explaining why those specific songs fit what the user described.

Input guardrails run before Stage 1: empty queries and queries over 500 characters are rejected immediately.

---

## 4. Data

The catalog is `data/songs.csv` — the same 10 songs from Module 3. No new data was added. The genre distribution (pop × 2, lofi × 3, rock × 1, ambient × 1, jazz × 1, synthwave × 1, indie pop × 1) has not changed.

---

## 5. Strengths

The retrieval step is fully transparent. Every recommendation includes the numeric score and the reasons behind it, so there is no mystery about why a song ranked where it did. This is a deliberate advantage over handing everything to an LLM, which would make the ranking process unpredictable across runs.

Claude handles input flexibility well. Queries with no genre reference at all ("something for homework") still produce reasonable structured preferences in most cases. The original rule-based system would have required a structured form input for this to work at all.

---

## 6. Limitations and Bias

The catalog bias from Module 3 carries forward. Genres with one song (jazz, rock, synthwave) will always return the same top result no matter how the query varies. Two users with completely different descriptions can get identical top picks if Claude maps both queries to the same genre.

Claude's parsing introduces its own inconsistency. The same query can return slightly different energy values across separate runs because the model doesn't deterministically pick a single float. Mood labels are also judgment calls — "focused" and "chill" often compete for the same queries. Exact-string matching in the eval harness catches these differences as failures even when the underlying interpretation was reasonable.

There is no feedback loop. The system has no way to learn that a user skipped the top recommendation or that the generated explanation missed the mark. Weights stay fixed across every query.

---

## 7. Evaluation Results

**Automated unit tests:** 7/7 passed. The 5 new tests in `tests/test_rag.py` mock the Claude calls so they run without an API key and verify pipeline structure, input validation, and retrieval behavior.

**Eval harness (`eval.py`):** 5 predefined end-to-end test cases run against the live API. Results across multiple runs: 4/5 passed consistently. The failing case was the "chill lofi studying" query, where Claude occasionally returned `focused` for mood instead of `chill`. Both interpretations are defensible, but the harness expects an exact match.

**Manual spot checks:** Three queries were tested by hand and the recommendations matched intuitions in each case. The moody synthwave query correctly surfaced Night Drive Loop as the top result. The acoustic jazz query put Coffee Shop Stories first by a wide margin. The high-energy gym query returned Storm Runner and Gym Hero at the top.

---

## 8. AI Collaboration Notes

Claude was used during development in two ways:

**Helpful:** When writing the JSON parsing logic in `src/llm.py`, Claude suggested stripping markdown code fences from the response before calling `json.loads`. This was something I would have caught only after hitting the error in testing — catching it early saved time.

**Flawed:** Claude suggested using Streamlit's `st.write_stream` for the generation step to show the response token by token as it streamed in. This broke because Streamlit's execution model reruns the entire script on each widget interaction, which interfered with the streaming iterator. The suggestion had to be reverted to a standard blocking `messages.create` call.

---

## 9. Reflection

The biggest thing this project reinforced is that a pipeline is only as good as its weakest link. The retriever is deterministic and consistent, but it's bottlenecked by a 10-song catalog. The LLM parser is flexible, but introduces variability that a rule-based parser wouldn't have. These two things pull in opposite directions and the right balance depends entirely on what you're optimizing for.

The eval harness was the most informative part of the build. Writing it forced me to define exactly what "correct" means for each test case, which turns out to be harder than it sounds when natural language is involved. It also made the catalog size problem concrete — with only 10 songs, a lot of the eval cases essentially test whether Claude can parse a query correctly, not whether the recommender is doing something interesting. Fixing that would require a bigger catalog.
