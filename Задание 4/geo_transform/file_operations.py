

def read_coordinates_from_file(filepath: str) -> list[tuple[float, float, float]]:
    """
    Читает координаты из текстового файла.
    Ожидаемый формат: по 3 числа в строке, разделенные пробелами/табами/запятыми.
    Примеры строк:
      1 2 3
      1, 2, 3
      1;2;3   (тоже поддержим)

    Возвращает список троек (a, b, c).
    """
    coords: list[tuple[float, float, float]] = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line_no, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue

            # поддержим разные разделители
            for sep in [",", ";"]:
                line = line.replace(sep, " ")
            parts = line.split()

            if len(parts) != 3:
                raise ValueError(
                    f"Строка {line_no}: ожидалось 3 числа, получено {len(parts)} -> {raw!r}"
                )

            a, b, c = (float(parts[0]), float(parts[1]), float(parts[2]))
            coords.append((a, b, c))

    return coords


def write_results_to_file(filepath: str, results: list[tuple[float, float, float]], header: str | None = None) -> None:
    """
    Записывает список троек в файл.
    Каждая строка: 'a b c' (с пробелами).
    """
    with open(filepath, "w", encoding="utf-8") as f:
        if header:
            f.write(f"# {header}\n")
        for a, b, c in results:
            f.write(f"{a} {b} {c}\n")
