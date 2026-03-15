import argparse
import sys
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
    ensure_dir,
    ensure_file,
    pdf_to_docx_one,
    pdf_to_docx_all,
    docx_to_pdf_one,
    docx_to_pdf_all,
    compress_one_image,
    compress_all_images,
    delete_group_files_noninteractive,
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


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Office_Tweaks",
        description="Office_Tweaks — утилиты для PDF/DOCX, сжатия изображений и удаления файлов.",
    )

    group = parser.add_mutually_exclusive_group(required=False)

    group.add_argument(
        "--pdf2docx",
        metavar="PATH|all",
        help='Конвертация PDF -> DOCX. Укажите путь к PDF или "all" для всех PDF в папке (--workdir).',
    )
    group.add_argument(
        "--docx2pdf",
        metavar="PATH|all",
        help='Конвертация DOCX -> PDF. Укажите путь к DOCX или "all" для всех DOCX в папке (--workdir).',
    )
    group.add_argument(
        "--compress-images",
        dest="compress_images",
        metavar="PATH|all",
        help='Сжатие изображений. Укажите путь к изображению или "all" для всех изображений в папке (--workdir).',
    )
    group.add_argument(
        "--delete",
        action="store_true",
        help="Удаление файлов по шаблону в указанной папке (--delete-dir).",
    )
    group.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Запуск в интерактивном режиме (меню).",
    )

    parser.add_argument(
        "--workdir",
        type=str,
        default=None,
        help="Рабочая папка (используется только для режима all).",
    )

    parser.add_argument(
        "--quality",
        type=int,
        choices=range(1, 101),
        default=75,
        help="Качество сжатия изображений (1..100), по умолчанию 75.",
    )

    parser.add_argument(
        "--delete-mode",
        choices=["startswith", "endswith", "contains", "extension"],
        default=None,
        help="Режим удаления: startswith|endswith|contains|extension",
    )
    parser.add_argument(
        "--delete-pattern",
        type=str,
        default=None,
        help="Подстрока/расширение для удаления (в зависимости от --delete-mode).",
    )
    parser.add_argument(
        "--delete-dir",
        type=str,
        default=None,
        help="Папка, в которой удалять файлы.",
    )

    return parser


def run_with_args(argv: list[str] | None = None) -> None:
    """
    Режим:
    - если нет аргументов или указан -i/--interactive -> интерактивное меню
    - иначе выполняем выбранную операцию и завершаемся
    """
    if argv is None:
        argv = sys.argv[1:]

    parser = _build_parser()

    # Если вообще не передали аргументов — интерактив.
    if not argv:
        run_cli()
        return

    args = parser.parse_args(argv)

    # Если явно попросили интерактив — интерактив.
    if args.interactive:
        run_cli()
        return

    # Определяем рабочую папку для all (если надо)
    workdir: Path | None = None
    if args.workdir is not None:
        workdir = ensure_dir(args.workdir)

    # --- PDF -> DOCX ---
    if args.pdf2docx is not None:
        target = args.pdf2docx.strip()
        if target.lower() == "all":
            wd = workdir or get_workdir()
            pdf_to_docx_all(wd)
        else:
            pdf_path = ensure_file(target)
            pdf_to_docx_one(pdf_path)
        return

    # --- DOCX -> PDF ---
    if args.docx2pdf is not None:
        target = args.docx2pdf.strip()
        if target.lower() == "all":
            wd = workdir or get_workdir()
            docx_to_pdf_all(wd)
        else:
            docx_path = ensure_file(target)
            docx_to_pdf_one(docx_path)
        return

    # --- Compress images ---
    if args.compress_images is not None:
        target = args.compress_images.strip()
        q: int = args.quality
        if target.lower() == "all":
            wd = workdir or get_workdir()
            compress_all_images(wd, quality=q)
        else:
            img_path = ensure_file(target)
            compress_one_image(img_path, quality=q)
        return

    # --- Delete ---
    if args.delete:
        if args.delete_dir is None:
            print("Ошибка: для --delete обязательно укажите --delete-dir")
            return
        if args.delete_mode is None:
            print("Ошибка: для --delete обязательно укажите --delete-mode (startswith|endswith|contains|extension)")
            return
        if args.delete_pattern is None or not args.delete_pattern.strip():
            print("Ошибка: для --delete обязательно укажите --delete-pattern")
            return

        delete_dir = ensure_dir(args.delete_dir)
        delete_group_files_noninteractive(
            delete_dir=delete_dir,
            mode=args.delete_mode,
            pattern=args.delete_pattern.strip(),
        )
        return

    # Если дошли сюда — операция не выбрана (например, передали только --workdir).
    # По ТЗ: если не указаны другие аргументы — интерактив.
    run_cli()
