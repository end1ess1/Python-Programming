
import math


class AngleConverter:
    @staticmethod
    def deg_to_rad(degrees: float) -> float:
        return degrees * math.pi / 180.0

    @staticmethod
    def rad_to_deg(radians: float) -> float:
        return radians * 180.0 / math.pi
