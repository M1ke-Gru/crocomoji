import httpx

JOKEAPI_URL = "https://v2.jokeapi.dev/joke/Any"

FALLBACK_SETUPS = [
    "Why don't scientists trust atoms?",
    "Why did the scarecrow win an award?",
    "Why can't you give Elsa a balloon?",
    "What do you call cheese that isn't yours?",
    "Why did the bicycle fall over?",
    "What do you call a fake noodle?",
    "Why did the math book look so sad?",
    "What do you call a sleeping dinosaur?",
    "Why did the golfer bring extra pants?",
    "What do you call a bear with no teeth?",
]
_fallback_index = 0


async def fetch_jokes(k: int) -> list[str]:
    """Fetch k joke setups (two-part jokes) from jokeapi.dev. Falls back on error."""
    setups: list[str] = []
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # jokeapi allows up to 10 per request
            while len(setups) < k:
                amount = min(10, k - len(setups))
                params = {"type": "twopart", "safe-mode": "", "amount": amount}
                resp = await client.get(JOKEAPI_URL, params=params)
                resp.raise_for_status()
                data = resp.json()

                if data.get("error"):
                    break

                if amount == 1:
                    # Single joke returned directly
                    if data.get("type") == "twopart":
                        setups.append(data["setup"])
                else:
                    for joke in data.get("jokes", []):
                        if joke.get("type") == "twopart":
                            setups.append(joke["setup"])
    except Exception:
        pass

    # Fill any gaps with fallbacks
    global _fallback_index
    while len(setups) < k:
        setups.append(FALLBACK_SETUPS[_fallback_index % len(FALLBACK_SETUPS)])
        _fallback_index += 1

    return setups[:k]
