import csv
import re
import sys
import urllib.request
from typing import List, Tuple


BASE_URL = "https://msk.spravker.ru/avtoservisy-avtotehcentry/"


def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64;"
            " AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/96.0.4664.110 Safari/537.36"
        ),
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request) as response:
        html_bytes = response.read()
        html = html_bytes.decode("utf-8", errors="ignore")
    return html


def parse_entries(html: str) -> List[Tuple[str, str, str, str]]:
    entries = []

    cleaned = re.sub(r"\s+", " ", html)

    listing_pattern = re.compile(
        r"<a[^>]*>(?P<name>[^<]+)</a>"
        r"[^<]*"
        r".*?"
        r"(?:</a>\s*)?"
        r"(?:</?[^>]+>)*"
        r"(?P<address>\b[^<]*?\d[^<]*)"
        r".*?"
        r"(?:Телефон[^<]*</?(?:span|div)[^>]*>\s*)?(?P<phones>(?:\+?\d|\(\d{3}\)).*?)"
        r".*?"
        r"(?:Часы работы[^<]*</?(?:span|div)[^>]*>\s*)?(?P<hours>[^<]{2,}?)"
        ,
        re.IGNORECASE
    )

    for match in listing_pattern.finditer(cleaned):
        name_raw = match.group("name") or ""
        address_raw = match.group("address") or ""
        phones_raw = match.group("phones") or ""
        hours_raw = match.group("hours") or ""

        def strip_tags(text: str) -> str:
            no_tags = re.sub(r"<[^>]+>", " ", text)
            return re.sub(r"\s+", " ", no_tags).strip()

        name = strip_tags(name_raw)
        address = strip_tags(address_raw)
        phones = strip_tags(phones_raw)
        hours = strip_tags(hours_raw)

        if name:
            entries.append((name, address, phones, hours))

    return entries


def save_to_csv(entries: List[Tuple[str, str, str, str]], filename: str) -> None:
    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Наименование", "Адрес", "Телефоны", "Часы работы"])
        writer.writerows(entries)


def main() -> None:
    try:
        html = fetch_html(BASE_URL)
    except Exception as exc:
        sys.stderr.write(f"Ошибка {BASE_URL}: {exc}\n")
        sys.exit(1)

    entries = parse_entries(html)
    if not entries:
        sys.stderr.write(
            "Предупреждение: ни одной записи не было найдено. Структура страницы могла измениться.\n"
        )

    output_file = "autocenters.csv"
    save_to_csv(entries, output_file)
    print(f"Сохранено {len(entries)} записей в {output_file}")

if __name__ == "__main__":
    main()