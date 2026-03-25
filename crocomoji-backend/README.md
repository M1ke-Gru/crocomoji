# Concept

A multiplayer party game where a narrator encodes a sentence using emojis, and teammates try to guess the sentence in text. An LLM evaluates the closeness of responses. The game is built around communication under constraint.

---

# Pre-Game: Story Generation

1. **Story LLM** generates a story with exactly `k = participants + 2` sentences
   - Each sentence must be longer than 5 words
   - Each sentence must extend upon the previous one
   - The story should involve some of the participants and sound interesting
2. **Perplexity LLM** assigns each sentence a guessability score `p_n ∈ [1, 100]`
   - Higher score = harder to guess
   - If any sentence scores `p_n > 80`, everything from that sentence onwards is sent back to the Story LLM for regeneration
3. **Normalized difficulty coefficient** for each sentence `n`:

$$q_n = \frac{p_n}{\sum_{i=1}^{k} p_i}$$

1. **Sentence score** (max total points across all sentences = 10,000):

$$s_n = q_n \times 10000$$

---

# Game Loop

## Roles

- One **narrator** per sentence, rotating each round
- All other players are **guessers**
- Number of sentences = number of participants + 2, so every player narrates at least once

## Narrator

- Sees the current sentence
- Encodes it using a limited number of emojis (count limit TBD, e.g. 3–5)
- Waits for guesser responses
- Selects the response they think is closest to the sentence
- Sends it to the LLM for evaluation
- Has **3 hits per sentence** — if the LLM rejects the selected response, the narrator can pick again
- After 3 failed hits, the round ends with no points awarded and the sentence is revealed

## Guessers

- See the narrator's emojis
- Submit text responses interpreting the sentence
- Can see each other's responses (social/bluffing dynamic)
- Keep submitting between narrator's LLM attempts

---

# Scoring

## Sentence Score `s_n`

Pre-calculated before the game based on difficulty (see Pre-Game above).

## Guesser Score

The LLM assigns a **closeness coefficient** `c_j ∈ [0, 1]` to each response selected by the narrator.

**Progression coefficient** for each selected attempt `j`:

$$a_j = c_j - c_{j-1}, \quad c_0 = 0$$

**Guesser score for sentence `n`** (only attempts selected by the narrator count, `r` resets each sentence):

$$u_n = s_n \cdot \sum_{j \in \text{selected}_n} a_j$$

**Total guesser score across the game:**

$$U = \sum_{n=1}^{k} u_n$$

## Narrator Score

$$N_n = \frac{s_n \cdot \sigma}{l}$$

- `σ` — closeness of the final accepted response to the actual sentence (0 to 1, assigned by LLM)
- `l` — number of responses submitted before the narrator accepted one for final evaluation

---

# Tech Stack

- **Backend:** FastAPI + WebSockets (Python), in-memory game state
- **Frontend:** Vue + Vite
- **LLM:** Anthropic API (story generation, perplexity scoring, closeness evaluation)
- **No database** — temporary game instances, no persistence needed for jam scope
