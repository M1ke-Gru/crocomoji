# Crocomoji Game Spec

## Concept

Crocomoji is a multiplayer party game where players finish jokes with their own endings.
The API is used only to get starting jokes.
Players decide which ending is the funniest by voting.

## Pre-Game Setup

1. Collect players in a room.
2. Gives a joke prompt using API jokeapi.dev:
3. Jokes have 2 parts. First one is setup from API and the second one is delivery from players.

## Round Flow

1. The active sentence is shown to all players.
2. During joke_time_seconds, each player submits one ending.
3. After submission time ends, all endings are revealed.
4. During voting_time_seconds, players vote for the funniest ending.
5. The ending with the most votes wins the round.
6. Move to the next sentence until all k sentences are played.

## Voting Rules

- Players cannot vote for their own ending.
- Each player gets one vote per round.
- Highest votes win the round. (We save all votes in score in leaderboard.)
- Suggested tie-breakers (choose one):
  - Split point across tied players.

## Scoring
- You get one point per vote and additional half point if all of other players voted for your joke
- Optional variant: each received vote gives points.
- Final winner is the player with the highest total points after all rounds.

## Room Rules Configuration
- Players can set up how many seconds they have to vote and create a joke

## Tech Stack

- Backend: FastAPI + WebSockets (Python), in-memory state
- Frontend: Vue + Vite
- API jokeapi.dev
- Persistence: none (jam scope)
