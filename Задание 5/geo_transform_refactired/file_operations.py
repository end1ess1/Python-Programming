
from dataclasses import dataclass
from typing import Iterable, Literal

from .transformations import CartesianCoordinate, SphericalCoordinate
from .utils import AngleConverter


AngleUnit = Literal["rad", "deg"]


@dataclass
class CoordinateFileManager:
    """
    Читает/пишет координаты из/в текстовый файл.

    Формат входного файла: в каждой строке 3 числа.
    Разделители: пробелы / табы / запятая / точка с запятой.
    Пустые строки и строки, начинающиеся с # — игнорируются.

    Для сферических координат можно указать единицы углов: rad или deg.
    """

    @staticmethod
    def _split_line(line: str) -> list[str]:
        for sep in [",", ";"]:
            line = line.replace(sep, " ")
        return line.split()

    def read_cartesian(self, filepath: str) -> list[CartesianCoordinate]:
        out: list[CartesianCoordinate] = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line_no, raw in enumerate(f, start=1):
                s = raw.strip()
                if not s or s.startswith("#"):
                    continue
                parts = self._split_line(s)
                if len(parts) != 3:
                    raise ValueError(f"Строка {line_no}: ожидалось 3 числа, получено {len(parts)} -> {raw!r}")
                x, y, z = map(float, parts)
                out.append(CartesianCoordinate(x, y, z))
        return out

    def read_spherical(self, filepath: str, angle_unit: AngleUnit = "rad") -> list[SphericalCoordinate]:
        out: list[SphericalCoordinate] = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line_no, raw in enumerate(f, start=1):
                s = raw.strip()
                if not s or s.startswith("#"):
                    continue
                parts = self._split_line(s)
                if len(parts) != 3:
                    raise ValueError(f"Строка {line_no}: ожидалось 3 числа, получено {len(parts)} -> {raw!r}")
                r, theta, phi = map(float, parts)

                if angle_unit == "deg":
                    theta = AngleConverter.deg_to_rad(theta)
                    phi = AngleConverter.deg_to_rad(phi)

                out.append(SphericalCoordinate(r=r, theta=theta, phi=phi))
        return out

    def write_cartesian(self, filepath: str, coords: Iterable[CartesianCoordinate], header: str | None = None) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            if header:
                f.write(f"# {header}\n")
            for p in coords:
                f.write(f"{p.x} {p.y} {p.z}\n")

    def write_spherical(
        self,
        filepath: str,
        coords: Iterable[SphericalCoordinate],
        header: str | None = None,
        angle_unit: AngleUnit = "rad",
    ) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            if header:
                f.write(f"# {header}\n")
            for s in coords:
                theta, phi = s.theta, s.phi
                if angle_unit == "deg":
                    theta = AngleConverter.rad_to_deg(theta)
                    phi = AngleConverter.rad_to_deg(phi)
                f.write(f"{s.r} {theta} {phi}\n")

