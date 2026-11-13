from math import sqrt


def wilson_interval(wins: int, losses: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de Wilson para una proporción. z=1.96 -> 95% de confianza."""
    n = wins + losses
    if n == 0:
        return (0.0, 1.0)  # sin datos: no sabemos nada

    p = wins / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z * sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def win_rate(wins: int, losses: int) -> float | None:
    n = wins + losses
    return wins / n if n else None