
import math


def cartesian_to_spherical(x: float, y: float, z: float) -> tuple[float, float, float]:
    """
    Декартовы (x, y, z) -> сферические (r, theta, phi)
    theta — азимутальный угол (в радианах)
    phi   — полярный угол (в радианах)

    Формулы из теории:
    r = sqrt(x^2 + y^2 + z^2)
    theta = 2 * atan2(y, x + sqrt(x^2 + y^2))
    phi = atan2(sqrt(x^2 + y^2), z)
    """
    r = math.sqrt(x * x + y * y + z * z)
    rho = math.sqrt(x * x + y * y)  # sqrt(x^2 + y^2)

    # theta (азимут)
    theta = 2.0 * math.atan2(y, x + rho)

    # phi (полярный)
    phi = math.atan2(rho, z)

    return r, theta, phi


def spherical_to_cartesian(r: float, theta: float, phi: float) -> tuple[float, float, float]:
    """
    Сферические (r, theta, phi) -> декартовы (x, y, z)
    Углы theta и phi должны быть в радианах.

    Формулы из теории:
    x = r * sin(phi) * cos(theta)
    y = r * sin(phi) * sin(theta)
    z = r * cos(phi)
    """
    x = r * math.sin(phi) * math.cos(theta)
    y = r * math.sin(phi) * math.sin(theta)
    z = r * math.cos(phi)
    return x, y, z
