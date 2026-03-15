from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable


# ---------------------------
# Ввод/каталог/списки файлов
# ---------------------------

def get_workdir() -> Path:
    return Path(os.getcwd())


def set_workdir(new_dir: str) -> Path:
    p = Path(new_dir).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"Каталог не найден: {p}")
    if not p.is_dir():
        raise NotADirectoryError(f"Это не каталог: {p}")
    os.chdir(p)
    return p


def list_files_by_ext(workdir: Path, exts: Iterable[str]) -> list[Path]:
    exts_norm = {e.lower().lstrip(".") for e in exts}
    files: list[Path] = []
    for item in workdir.iterdir():
        if item.is_file() and item.suffix.lower().lstrip(".") in exts_norm:
            files.append(item)
    files.sort(key=lambda p: p.name.lower())
    return files


def print_numbered(files: list[Path], title: str) -> None:
    print(title)
    if not files:
        print("  (файлы не найдены)")
        return
    for i, f in enumerate(files, start=1):
        print(f"{i}. {f.name}")


def ask_int(prompt: str, min_value: int | None = None, max_value: int | None = None) -> int:
    while True:
        s = input(prompt).strip()
        try:
            v = int(s)
        except ValueError:
            print("Введите целое число.")
            continue

        if min_value is not None and v < min_value:
            print(f"Число должно быть >= {min_value}.")
            continue
        if max_value is not None and v > max_value:
            print(f"Число должно быть <= {max_value}.")
            continue
        return v


def ask_path(prompt: str) -> str:
    return input(prompt).strip()


def choose_file_or_all(files: list[Path]) -> list[Path]:
    """
    По ТЗ: введите номер файла, либо 0 — чтобы обработать все файлы.
    """
    if not files:
        return []
    n = ask_int("Введите номер файла (0 — обработать все): ", min_value=0, max_value=len(files))
    if n == 0:
        return files
    return [files[n - 1]]


# ---------------------------
# Проверки для argparse-режима
# ---------------------------

def ensure_dir(path_str: str) -> Path:
    p = Path(path_str).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"Каталог не найден: {p}")
    if not p.is_dir():
        raise NotADirectoryError(f"Это не каталог: {p}")
    return p


def ensure_file(path_str: str) -> Path:
    p = Path(path_str).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"Файл не найден: {p}")
    if not p.is_file():
        raise FileNotFoundError(f"Это не файл: {p}")
    return p


# ---------------------------
# PDF -> DOCX (интерактив)
# ---------------------------

def convert_pdf_to_docx(workdir: Path) -> None:
    try:
        from pdf2docx import Converter  # type: ignore
    except ImportError:
        print("Ошибка: модуль pdf2docx не установлен. Установите: pip install pdf2docx")
        return

    pdf_files = list_files_by_ext(workdir, ["pdf"])
    print_numbered(pdf_files, f"\nСписок файлов с расширением .pdf в каталоге: {workdir}")
    targets = choose_file_or_all(pdf_files)
    if not targets:
        return

    for pdf_path in targets:
        docx_path = pdf_path.with_suffix(".docx")
        try:
            cv = Converter(str(pdf_path))
            try:
                cv.convert(str(docx_path))
            finally:
                cv.close()
            print(f"Готово: {pdf_path.name} -> {docx_path.name}")
        except Exception as e:
            print(f"Ошибка при конвертации {pdf_path.name}: {e}")


# ---------------------------
# DOCX -> PDF (интерактив)
# ---------------------------

def convert_docx_to_pdf(workdir: Path) -> None:
    try:
        from docx2pdf import convert  # type: ignore
    except ImportError:
        print("Ошибка: модуль docx2pdf не установлен. Установите: pip install docx2pdf")
        return

    docx_files = list_files_by_ext(workdir, ["docx"])
    print_numbered(docx_files, f"\nСписок файлов с расширением .docx в каталоге: {workdir}")
    targets = choose_file_or_all(docx_files)
    if not targets:
        return

    for docx_path in targets:
        pdf_path = docx_path.with_suffix(".pdf")
        try:
            convert(str(docx_path), str(pdf_path))
            print(f"Готово: {docx_path.name} -> {pdf_path.name}")
        except Exception as e:
            print(f"Ошибка при конвертации {docx_path.name}: {e}")


# ---------------------------
# Сжатие изображений (интерактив)
# ---------------------------

def compress_images(workdir: Path) -> None:
    try:
        from PIL import Image  # type: ignore
    except ImportError:
        print("Ошибка: модуль Pillow не установлен. Установите: pip install Pillow")
        return

    img_files = list_files_by_ext(workdir, ["jpg", "jpeg", "png", "gif"])
    print_numbered(img_files, f"\nСписок изображений (.jpeg/.gif/.png/.jpg) в каталоге: {workdir}")
    targets = choose_file_or_all(img_files)
    if not targets:
        return

    quality = ask_int("Введите параметр сжатия (от 1 до 100%): ", min_value=1, max_value=100)

    for img_path in targets:
        try:
            out_path = img_path.with_name(f"{img_path.stem}_compressed{img_path.suffix}")

            with Image.open(img_path) as im:
                fmt = (im.format or img_path.suffix.lstrip(".")).upper()
                save_kwargs = {}

                if fmt in {"JPG", "JPEG"}:
                    save_kwargs["quality"] = quality
                    save_kwargs["optimize"] = True

                elif fmt == "PNG":
                    save_kwargs["optimize"] = True
                    # Чем ниже quality, тем сильнее сжатие (уровень 9), чем выше — тем слабее (уровень 0).
                    compress_level = int(round(9 * (1 - quality / 100)))
                    save_kwargs["compress_level"] = max(0, min(9, compress_level))

                elif fmt == "GIF":
                    save_kwargs["optimize"] = True

                im.save(out_path, **save_kwargs)

            print(f"Готово: {img_path.name} -> {out_path.name}")
        except Exception as e:
            print(f"Ошибка при обработке {img_path.name}: {e}")


# ---------------------------
# Удаление группы файлов (интерактив)
# ---------------------------

def delete_group_files(workdir: Path) -> None:
    print("\nВыберите действие:")
    print("1. Удалить все файлы, начинающиеся на определенную подстроку")
    print("2. Удалить все файлы, заканчивающиеся на определенную подстроку")
    print("3. Удалить все файлы, содержащие определенную подстроку")
    print("4. Удалить все файлы по расширению")

    choice = ask_int("Введите номер действия: ", min_value=1, max_value=4)

    try:
        items = [p for p in workdir.iterdir() if p.is_file()]
    except Exception as e:
        print(f"Ошибка чтения каталога {workdir}: {e}")
        return

    if choice in (1, 2, 3):
        sub = input("Введите подстроку: ").strip()
        if not sub:
            print("Подстрока пустая — отмена.")
            return

        if choice == 1:
            to_delete = [p for p in items if p.name.startswith(sub)]
        elif choice == 2:
            to_delete = [p for p in items if p.name.endswith(sub)]
        else:
            to_delete = [p for p in items if sub in p.name]

    else:
        ext = input("Введите расширение (например: docx или .docx): ").strip().lower()
        ext = ext.lstrip(".")
        if not ext:
            print("Расширение пустое — отмена.")
            return
        to_delete = [p for p in items if p.suffix.lower().lstrip(".") == ext]

    if not to_delete:
        print("Подходящих файлов не найдено.")
        return

    for p in to_delete:
        try:
            p.unlink()
            print(f'Файл: "{p.name}" успешно удалён!')
        except Exception as e:
            print(f'Не удалось удалить "{p.name}": {e}')


# ==========================================================
#          НЕИНТЕРАКТИВНЫЕ ФУНКЦИИ (для argparse)
# ==========================================================

# --- PDF -> DOCX (one/all) ---

def pdf_to_docx_one(pdf_path: Path) -> None:
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Ожидался PDF файл, получено: {pdf_path.name}")

    try:
        from pdf2docx import Converter  # type: ignore
    except ImportError:
        print("Ошибка: модуль pdf2docx не установлен. Установите: pip install pdf2docx")
        return

    docx_path = pdf_path.with_suffix(".docx")
    try:
        cv = Converter(str(pdf_path))
        try:
            cv.convert(str(docx_path))
        finally:
            cv.close()
        print(f"Готово: {pdf_path.name} -> {docx_path.name}")
    except Exception as e:
        print(f"Ошибка при конвертации {pdf_path.name}: {e}")


def pdf_to_docx_all(workdir: Path) -> None:
    pdf_files = list_files_by_ext(workdir, ["pdf"])
    if not pdf_files:
        print(f"PDF файлы в папке не найдены: {workdir}")
        return
    for p in pdf_files:
        pdf_to_docx_one(p)


# --- DOCX -> PDF (one/all) ---

def docx_to_pdf_one(docx_path: Path) -> None:
    if docx_path.suffix.lower() != ".docx":
        raise ValueError(f"Ожидался DOCX файл, получено: {docx_path.name}")

    try:
        from docx2pdf import convert  # type: ignore
    except ImportError:
        print("Ошибка: модуль docx2pdf не установлен. Установите: pip install docx2pdf")
        return

    pdf_path = docx_path.with_suffix(".pdf")
    try:
        convert(str(docx_path), str(pdf_path))
        print(f"Готово: {docx_path.name} -> {pdf_path.name}")
    except Exception as e:
        print(f"Ошибка при конвертации {docx_path.name}: {e}")


def docx_to_pdf_all(workdir: Path) -> None:
    docx_files = list_files_by_ext(workdir, ["docx"])
    if not docx_files:
        print(f"DOCX файлы в папке не найдены: {workdir}")
        return
    for p in docx_files:
        docx_to_pdf_one(p)


# --- Compress images (one/all) ---

def compress_one_image(img_path: Path, quality: int = 75) -> None:
    if quality < 1 or quality > 100:
        raise ValueError("quality должен быть в диапазоне 1..100")

    if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".gif"}:
        raise ValueError(f"Неподдерживаемый формат изображения: {img_path.name}")

    try:
        from PIL import Image  # type: ignore
    except ImportError:
        print("Ошибка: модуль Pillow не установлен. Установите: pip install Pillow")
        return

    out_path = img_path.with_name(f"{img_path.stem}_compressed{img_path.suffix}")

    try:
        with Image.open(img_path) as im:
            fmt = (im.format or img_path.suffix.lstrip(".")).upper()
            save_kwargs = {}

            if fmt in {"JPG", "JPEG"}:
                save_kwargs["quality"] = quality
                save_kwargs["optimize"] = True

            elif fmt == "PNG":
                save_kwargs["optimize"] = True
                compress_level = int(round(9 * (1 - quality / 100)))
                save_kwargs["compress_level"] = max(0, min(9, compress_level))

            elif fmt == "GIF":
                save_kwargs["optimize"] = True

            im.save(out_path, **save_kwargs)

        print(f"Готово: {img_path.name} -> {out_path.name}")
    except Exception as e:
        print(f"Ошибка при обработке {img_path.name}: {e}")


def compress_all_images(workdir: Path, quality: int = 75) -> None:
    img_files = list_files_by_ext(workdir, ["jpg", "jpeg", "png", "gif"])
    if not img_files:
        print(f"Изображения в папке не найдены: {workdir}")
        return
    for p in img_files:
        compress_one_image(p, quality=quality)


# --- Delete group files (non-interactive) ---

def delete_group_files_noninteractive(delete_dir: Path, mode: str, pattern: str) -> None:
    if not pattern:
        print("Ошибка: delete-pattern пустой.")
        return

    try:
        items = [p for p in delete_dir.iterdir() if p.is_file()]
    except Exception as e:
        print(f"Ошибка чтения каталога {delete_dir}: {e}")
        return

    if mode == "startswith":
        to_delete = [p for p in items if p.name.startswith(pattern)]
    elif mode == "endswith":
        to_delete = [p for p in items if p.name.endswith(pattern)]
    elif mode == "contains":
        to_delete = [p for p in items if pattern in p.name]
    elif mode == "extension":
        ext = pattern.lower().lstrip(".")
        if not ext:
            print("Ошибка: для mode=extension pattern должен быть расширением (например docx или .docx).")
            return
        to_delete = [p for p in items if p.suffix.lower().lstrip(".") == ext]
    else:
        print(f"Ошибка: неизвестный delete-mode: {mode}")
        return

    if not to_delete:
        print("Подходящих файлов не найдено.")
        return

    for p in to_delete:
        try:
            p.unlink()
            print(f'Файл: "{p.name}" успешно удалён!')
        except Exception as e:
            print(f'Не удалось удалить "{p.name}": {e}')
