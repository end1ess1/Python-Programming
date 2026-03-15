
from .transformations import CartesianCoordinate, SphericalCoordinate, CoordinateTransformer
from .utils import AngleConverter
from .file_operations import CoordinateFileManager


def _ask_float(prompt: str) -> float:
    while True:
        s = input(prompt).strip().replace(",", ".")
        try:
            return float(s)
        except ValueError:
            print("Введите число, например: 1.5")


def _ask_choice(title: str, options: dict[str, str]) -> str:
    while True:
        print(title)
        for k, v in options.items():
            print(f"  {k} — {v}")
        ans = input("Ваш выбор: ").strip()
        if ans in options:
            return ans
        print("Неверный выбор.\n")


def main() -> None:
    print("=== geo_transform (ООП) ===\n")

    action = _ask_choice(
        "Что делаем?",
        {"1": "Декартовы -> сферические", "2": "Сферические -> декартовы"},
    )

    source = _ask_choice(
        "\nОткуда берём данные?",
        {"1": "Ввод вручную (одна точка)", "2": "Чтение из файла (много строк)"},
    )

    fm = CoordinateFileManager()

    if action == "2":
        angle_unit = _ask_choice("\nЕдиницы углов theta и phi:", {"1": "радианы", "2": "градусы"})
        angle_unit = "deg" if angle_unit == "2" else "rad"

    if source == "1":
        if action == "1":
            p = CartesianCoordinate(_ask_float("x = "), _ask_float("y = "), _ask_float("z = "))
            s = CoordinateTransformer.cartesian_to_spherical(p)

            show = _ask_choice("\nПоказать углы:", {"1": "в радианах", "2": "в градусах"})
            if show == "2":
                print(
                    f"\nr={s.r}, theta={AngleConverter.rad_to_deg(s.theta)}, phi={AngleConverter.rad_to_deg(s.phi)}"
                )
            else:
                print(f"\nr={s.r}, theta={s.theta}, phi={s.phi}")

        else:
            s = SphericalCoordinate(_ask_float("r = "), _ask_float("theta = "), _ask_float("phi = "))
            if angle_unit == "deg":
                s.theta = AngleConverter.deg_to_rad(s.theta)
                s.phi = AngleConverter.deg_to_rad(s.phi)

            p = CoordinateTransformer.spherical_to_cartesian(s)
            print(f"\nx={p.x}, y={p.y}, z={p.z}")

        return

    # source == "2" (из файла)
    in_path = input("\nПуть к входному файлу: ").strip()

    if action == "1":
        cart_list = fm.read_cartesian(in_path)
        sph_list = [CoordinateTransformer.cartesian_to_spherical(p) for p in cart_list]

        out_where = _ask_choice("\nКуда вывести результат?", {"1": "на экран", "2": "в файл"})
        if out_where == "1":
            show = _ask_choice("\nПоказать углы:", {"1": "в радианах", "2": "в градусах"})
            for s in sph_list:
                if show == "2":
                    print((s.r, AngleConverter.rad_to_deg(s.theta), AngleConverter.rad_to_deg(s.phi)))
                else:
                    print((s.r, s.theta, s.phi))
        else:
            out_path = input("Путь к файлу для записи: ").strip()
            out_unit = _ask_choice("\nЗаписать углы:", {"1": "в радианах", "2": "в градусах"})
            out_unit = "deg" if out_unit == "2" else "rad"
            fm.write_spherical(out_path, sph_list, header="Результаты: cartesian -> spherical", angle_unit=out_unit)
            print(f"Готово! Записано в: {out_path}")

    else:
        sph_list = fm.read_spherical(in_path, angle_unit=angle_unit)
        cart_list = [CoordinateTransformer.spherical_to_cartesian(s) for s in sph_list]

        out_where = _ask_choice("\nКуда вывести результат?", {"1": "на экран", "2": "в файл"})
        if out_where == "1":
            for p in cart_list:
                print((p.x, p.y, p.z))
        else:
            out_path = input("Путь к файлу для записи: ").strip()
            fm.write_cartesian(out_path, cart_list, header="Результаты: spherical -> cartesian")
            print(f"Готово! Записано в: {out_path}")

    print("\n=== Конец работы ===")


if __name__ == "__main__":
    main()
