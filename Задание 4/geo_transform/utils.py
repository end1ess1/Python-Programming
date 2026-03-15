
import math


def deg_to_rad(degrees: float) -> float:
    """Градусы -> радианы."""
    return degrees * math.pi / 180.0


def rad_to_deg(radians: float) -> float:
    """Радианы -> градусы."""
    return radians * 180.0 / math.pi
