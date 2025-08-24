import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import json
from io import BytesIO
import re

BASE_URL = "https://mindev.gov.ua/"
PAGE_URL = "https://mindev.gov.ua/diialnist/rozvytok-mistsevoho-samovriaduvannia/kodyfikator-administratyvno-terytorialnykh-odynyts-ta-terytorii-terytorialnykh-hromad"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": BASE_URL,
}


def get_latest_entry():
    try:
        resp = requests.get(PAGE_URL, headers=HEADERS)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTPError: {e}\nResponse content: {resp.text}")
        raise
    soup = BeautifulSoup(resp.text, "html.parser")

    # шукаємо всі <p> з посиланнями на накази
    entries = []
    for p in soup.find_all("p"):
        pdf_link = p.find("a", href=lambda h: h and h.endswith(".pdf"))
        xlsx_link = p.find_next("a", href=lambda h: h and h.endswith(".xlsx"))

        if pdf_link and xlsx_link:
            text = pdf_link.get_text(strip=True)
            pdf_url = urljoin(BASE_URL, pdf_link["href"])
            xlsx_url = urljoin(BASE_URL, xlsx_link["href"])

            # витягуємо номер і дату наказу
            m = re.search(r"№\s*(\d+)", text)
            order_number = m.group(1) if m else None

            m_date = re.search(r"від\s+(\d{1,2})\s+([а-яА-ЯіїєґІЇЄҐ]+)\s+(\d{4})", text)
            order_date = m_date.group(0).replace("від", "").strip() if m_date else None

            entries.append(
                {
                    "order_title": text,
                    "order_number": order_number,
                    "order_date": order_date,
                    "pdf_url": pdf_url,
                    "xlsx_url": xlsx_url,
                }
            )
    if not entries:
        raise Exception("Не вдалося знайти жодного наказу з XLSX")
    return entries[0]


def parse_xlsx_to_json(entry, save_as="core/tools/location/kodifikator.json"):
    resp = requests.get(entry["xlsx_url"], headers=HEADERS)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTPError: {e}\nResponse content: {resp.text}")
        raise

    excel_data = pd.ExcelFile(BytesIO(resp.content))
    df = pd.read_excel(excel_data, sheet_name="Кодифікатор")
    df = df.drop(index=[0, 1, 2])
    df.columns = [
        "level1",
        "level2",
        "level3",
        "level4",
        "level_extra",
        "category",
        "name",
    ]
    df = df.reset_index(drop=True)

    result = {
        "provider": {
            "name": "Міністерство розвитку громад, територій та інфраструктури України",
            "service": "Кодифікатор адміністративно-територіальних одиниць",
            "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        },
        "order": {
            "title": entry["order_title"],
            "number": entry["order_number"],
            "date": entry["order_date"],
            "pdf_url": entry["pdf_url"],
        },
        "data": df.to_dict(orient="records"),
    }

    with open(save_as, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return save_as


async def download_xlsx_and_parse_to_json():
    latest_entry = get_latest_entry()
    print(f"Знайдено наказ: {latest_entry['order_title']}")
    saved_json = parse_xlsx_to_json(latest_entry)
    print(f"✅ JSON збережено у {saved_json}")
    return {"status": 200, "detail": "Kodifier has been updated"}
