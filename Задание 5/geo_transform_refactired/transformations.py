
from dataclasses import dataclass
import math


@dataclass
class CartesianCoordinate:
    x: float
    y: float
    z: float


@dataclass
class SphericalCoordinate:
    r: float
    theta: float  # азимут (радианы)
    phi: float    # полярный (радианы)


class CoordinateTransformer:
    """
    Преобразования между декартовыми и сферическими координатами.

    Используются формулы из теории:
    r = sqrt(x^2 + y^2 + z^2)
    theta = 2 * atan2(y, x + sqrt(x^2 + y^2))
    phi = atan2(sqrt(x^2 + y^2), z)

    x = r * sin(phi) * cos(theta)
    y = r * sin(phi) * sin(theta)
    z = r * cos(phi)
    """

    @staticmethod
    def cartesian_to_spherical(p: CartesianCoordinate) -> SphericalCoordinate:
        x, y, z = p.x, p.y, p.z
        r = math.sqrt(x * x + y * y + z * z)
        rho = math.sqrt(x * x + y * y)

        theta = 2.0 * math.atan2(y, x + rho)
        phi = math.atan2(rho, z)

        return SphericalCoordinate(r=r, theta=theta, phi=phi)

    @staticmethod
    def spherical_to_cartesian(s: SphericalCoordinate) -> CartesianCoordinate:
        r, theta, phi = s.r, s.theta, s.phi
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.sin(phi) * math.sin(theta)
        z = r * math.cos(phi)
        return CartesianCoordinate(x=x, y=y, z=z)
