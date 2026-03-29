import httpx

JOKEAPI_URL = "https://v2.jokeapi.dev/joke/Any"

FALLBACK_JOKES = [
    {"setup": "Why don't scientists trust atoms?", "delivery": "Because they make up everything."},
    {"setup": "Why did the scarecrow win an award?", "delivery": "Because he was outstanding in his field."},
    {"setup": "Why can't you give Elsa a balloon?", "delivery": "Because she will let it go."},
    {"setup": "What do you call cheese that isn't yours?", "delivery": "Nacho cheese."},
    {"setup": "Why did the bicycle fall over?", "delivery": "Because it was two-tired."},
    {"setup": "What do you call a fake noodle?", "delivery": "An impasta."},
    {"setup": "Why did the math book look so sad?", "delivery": "Because it had too many problems."},
    {"setup": "What do you call a sleeping dinosaur?", "delivery": "A dino-snore."},
    {"setup": "Why did the golfer bring extra pants?", "delivery": "In case he got a hole in one."},
    {"setup": "What do you call a bear with no teeth?", "delivery": "A gummy bear."},
]
_fallback_index = 0


async def fetch_jokes(k: int) -> list[dict[str, str]]:
    """Fetch k two-part jokes from jokeapi.dev. Falls back on error."""
    jokes: list[dict[str, str]] = []
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # jokeapi allows up to 10 per request
            while len(jokes) < k:
                amount = min(10, k - len(jokes))
                params = {"type": "twopart", "safe-mode": "", "amount": amount}
                resp = await client.get(JOKEAPI_URL, params=params)
                resp.raise_for_status()
                data = resp.json()

                if data.get("error"):
                    break

                if amount == 1:
                    # Single joke returned directly
                    if data.get("type") == "twopart":
                        jokes.append(
                            {
                                "setup": data.get("setup", ""),
                                "delivery": data.get("delivery", ""),
                            }
                        )
                else:
                    for joke in data.get("jokes", []):
                        if joke.get("type") == "twopart":
                            jokes.append(
                                {
                                    "setup": joke.get("setup", ""),
                                    "delivery": joke.get("delivery", ""),
                                }
                            )
    except Exception:
        pass

    # Fill any gaps with fallbacks
    global _fallback_index
    while len(jokes) < k:
        jokes.append(FALLBACK_JOKES[_fallback_index % len(FALLBACK_JOKES)])
        _fallback_index += 1

    return jokes[:k]
