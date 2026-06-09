import random

def exponential_backoff(attempt: int, base: float = 1.0, max_delay: float = 60.0) -> float:
    """
    Exponential backoff with jitter. Returns delay in seconds.
    """
    delay = min(base * (2 ** attempt), max_delay)
    jitter = random.uniform(0, delay * 0.5)
    return delay + jitter
