# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

This system suggests up to 5 songs from a small 10-song catalog based on a user's preferred genre, mood, energy level, and whether they like acoustic music. It is built for classroom exploration only and is not meant for real users or a production environment.

---

## 3. How the Model Works

Every song in the catalog gets a score based on how well it matches what the user said they like. Genre match adds the most points, followed by mood match. Then the system looks at energy: if a song's energy level is far from what the user wants, it loses points. Songs that are very acoustic get a bonus if the user likes acoustic music, or a small penalty if they don't. Finally, a song's valence (how positive or upbeat it sounds) adds a tiny bonus on top of everything else. Once every song has a score, they get sorted from highest to lowest and the top results are returned.

---

## 4. Data

There are 10 songs in `data/songs.csv`. I kept the original catalog without adding or removing any songs. The genres represented are pop, lofi, rock, ambient, jazz, synthwave, and indie pop. The moods include happy, chill, intense, relaxed, focused, and moody. The catalog leans toward chill and electronic styles with 3 lofi or ambient tracks out of 10. There is only one jazz track and one rock track, so users who prefer those genres don't have much variety to pick from. The data mostly reflects the kind of music that tends to appear in study playlists or background listening contexts.

---

## 5. Strengths

The system works well for users whose preferences match genres that have more than one representative song in the catalog. A pop or lofi user gets a reasonable ranked list where the top pick genuinely fits their taste. The scoring logic is transparent and easy to follow: you can look at any recommendation and understand exactly why it ranked where it did. It also handles edge cases cleanly, like a user who likes acoustic music getting acoustic tracks pushed to the top rather than being buried by high-energy songs.

---

## 6. Limitations and Bias

The system ignores tempo as a ranking factor even though tempo is one of the clearest signals of whether a song fits a workout versus a study session. It also treats genre as a single exact match, so a user who likes "indie pop" gets no credit for "pop" songs even though the two genres overlap a lot.

The catalog itself introduces bias. With only one jazz song and one rock song, users who prefer those genres will always get the same top result. There is no diversity mechanism, so the top 5 for a pop fan will look almost identical to another pop fan even if their moods and energy targets differ. If this were used in a real product, it would quietly push users toward whatever genres had the most catalog coverage, rewarding the majority taste and underserving everyone else.

---

## 7. Evaluation

I tested three different user profiles manually and checked whether the results matched my intuitions:

1. Pop/happy/high energy user: "Sunrise City" came first by a wide margin, followed by "Gym Hero." That order felt right since both are upbeat pop tracks and Sunrise City has a mood match on top of the genre match.

2. Lofi/chill/low energy user: "Library Rain" and "Midnight Coding" both ranked at the top. Those are exactly the two tracks you'd expect for that profile.

3. Jazz/relaxed/low energy/likes acoustic user: "Coffee Shop Stories" ranked first with a significant lead, which made sense since it matched genre, mood, and had high acousticness.

I also ran the two automated tests in the test file. Both passed, confirming that the class-based recommender sorts correctly and produces non-empty explanations.

---

## 8. Future Work

Adding tempo as a scoring feature would make the system more useful for people who are looking for something at a specific pace. A user training for a run has very different tempo needs than someone studying. It would also help to replace the binary acoustic preference with a continuous slider so users could say "somewhat acoustic" instead of just yes or no. On the catalog side, expanding to at least 3 to 5 songs per genre would make recommendations feel less predictable. A longer-term improvement would be tracking which songs a user skips so the weights could adjust over time rather than staying fixed.

---

## 9. Personal Reflection

The part that surprised me most was how a small change to one weight could completely change the output. Lowering the genre weight by 2 points turned the results from "clearly sorted by taste" to "almost random-feeling" because energy started dominating. That made me think about how much power the people building real recommendation systems have. Every time Spotify or YouTube tweaks a weight, millions of people's feeds change and most of them have no idea it happened.

I also didn't expect the catalog size to matter so much. I assumed the scoring logic would be the hard part, but having only 10 songs meant the algorithm barely had room to do anything interesting. Real recommenders work because they have millions of options to sort through. That gap between a classroom simulation and a deployed product is a lot bigger than I thought going in.
