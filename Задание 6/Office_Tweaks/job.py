from pathlib import Path

from .utils import (
    get_workdir,
    set_workdir,
    ask_int,
    ask_path,
    convert_pdf_to_docx,
    convert_docx_to_pdf,
    compress_images,
    delete_group_files,
)


def print_menu() -> None:
    print("\nВыберите действие:")
    print("0. Сменить рабочий каталог")
    print("1. Преобразовать PDF в Docx")
    print("2. Преобразовать Docx в PDF")
    print("3. Произвести сжатие изображений")
    print("4. Удалить группу файлов")
    print("5. Выход")


def run_cli() -> None:
    while True:
        workdir: Path = get_workdir()
        print(f"\nТекущий каталог: {workdir}")

        print_menu()
        action = ask_int("Ваш выбор: ", min_value=0, max_value=5)

        if action == 5:
            print("Выход.")
            return

        if action == 0:
            new_dir = ask_path("Укажите полный путь к рабочему каталогу: ")
            try:
                set_workdir(new_dir)
            except Exception as e:
                print(f"Ошибка смены каталога: {e}")
            continue

        # Защита от неожиданных сбоев, чтобы меню продолжало работать
        try:
            if action == 1:
                convert_pdf_to_docx(get_workdir())
            elif action == 2:
                convert_docx_to_pdf(get_workdir())
            elif action == 3:
                compress_images(get_workdir())
            elif action == 4:
                delete_group_files(get_workdir())
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
