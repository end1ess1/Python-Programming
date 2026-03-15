
from .transformations import cartesian_to_spherical, spherical_to_cartesian
from .utils import deg_to_rad, rad_to_deg
from .file_operations import read_coordinates_from_file, write_results_to_file


def _ask_float(prompt: str) -> float:
    while True:
        s = input(prompt).strip().replace(",", ".")
        try:
            return float(s)
        except ValueError:
            print("Введите число (например 1.5).")


def _ask_choice(prompt: str, choices: dict[str, str]) -> str:
    """
    choices: {"1": "описание", ...}
    """
    while True:
        print(prompt)
        for k, v in choices.items():
            print(f"  {k} — {v}")
        ans = input("Ваш выбор: ").strip()
        if ans in choices:
            return ans
        print("Неверный выбор, попробуйте снова.\n")


def _convert_angles_if_needed(theta: float, phi: float, unit_choice: str) -> tuple[float, float]:
    # unit_choice: "1" radians, "2" degrees
    if unit_choice == "2":
        return deg_to_rad(theta), deg_to_rad(phi)
    return theta, phi


def _format_spherical(r: float, theta: float, phi: float, show_degrees: bool) -> tuple[float, float, float]:
    if show_degrees:
        return r, rad_to_deg(theta), rad_to_deg(phi)
    return r, theta, phi


def main() -> None:
    print("=== geo_transform: преобразование координат ===\n")

    mode = _ask_choice(
        "Что делаем?",
        {
            "1": "Декартовы -> сферические",
            "2": "Сферические -> декартовы",
        },
    )

    input_mode = _ask_choice(
        "\nКак вводим данные?",
        {
            "1": "Вручную (одна тройка)",
            "2": "Из файла (много строк по 3 числа)",
        },
    )

    # для сферических: спросим единицы измерения углов
    angle_unit = None
    if mode == "2":
        angle_unit = _ask_choice(
            "\nЕдиницы углов theta и phi:",
            {"1": "радианы", "2": "градусы"},
        )

    results: list[tuple[float, float, float]] = []

    if input_mode == "1":
        if mode == "1":
            x = _ask_float("x = ")
            y = _ask_float("y = ")
            z = _ask_float("z = ")
            r, theta, phi = cartesian_to_spherical(x, y, z)

            show = _ask_choice("\nПоказать углы:", {"1": "в радианах", "2": "в градусах"})
            r2, t2, p2 = _format_spherical(r, theta, phi, show_degrees=(show == "2"))
            print(f"\n(r, theta, phi) = ({r2}, {t2}, {p2})")
            results.append((r2, t2, p2))

        else:
            r = _ask_float("r = ")
            theta = _ask_float("theta = ")
            phi = _ask_float("phi = ")

            theta, phi = _convert_angles_if_needed(theta, phi, angle_unit)
            x, y, z = spherical_to_cartesian(r, theta, phi)

            print(f"\n(x, y, z) = ({x}, {y}, {z})")
            results.append((x, y, z))

    else:
        in_path = input("\nПуть к входному файлу: ").strip()
        coords = read_coordinates_from_file(in_path)

        if mode == "1":
            show = _ask_choice("\nПоказать углы:", {"1": "в радианах", "2": "в градусах"})
            show_deg = (show == "2")

            for x, y, z in coords:
                r, theta, phi = cartesian_to_spherical(x, y, z)
                results.append(_format_spherical(r, theta, phi, show_degrees=show_deg))

        else:
            for r, theta, phi in coords:
                theta, phi = _convert_angles_if_needed(theta, phi, angle_unit)
                results.append(spherical_to_cartesian(r, theta, phi))

        out_choice = _ask_choice("\nКуда вывести результат?", {"1": "на экран", "2": "в файл"})
        if out_choice == "1":
            print("\nРезультаты:")
            for triple in results:
                print(triple)
        else:
            out_path = input("Путь к файлу для записи: ").strip()
            header = "Результаты преобразования geo_transform"
            write_results_to_file(out_path, results, header=header)
            print(f"Готово! Записано в: {out_path}")

    print("\n=== Конец работы ===")


if __name__ == "__main__":
    main()
