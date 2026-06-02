import time
import csv
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "STAT418 student project - educational use"
}

category_urls = [
    "https://www.ikea.com/us/en/cat/bookcases-10382/",
    "https://www.ikea.com/us/en/cat/tables-desks-fu004/",
    "https://www.ikea.com/us/en/cat/sofas-fu003/",
    "https://www.ikea.com/us/en/cat/beds-bm003/",
    "https://www.ikea.com/us/en/cat/chairs-fu002/",
    "https://www.ikea.com/us/en/cat/dressers-storage-drawers-st004/",
    "https://www.ikea.com/us/en/cat/tv-media-furniture-10475/",
    "https://www.ikea.com/us/en/cat/storage-organization-st001/",
    "https://www.ikea.com/us/en/cat/cabinets-cupboards-st003/",
    "https://www.ikea.com/us/en/cat/outdoor-furniture-od003/",
]

rows = []

for category_url in category_urls:
    print("Collecting:", category_url)

    response = requests.get(category_url, headers=headers, timeout=20)
    print("status:", response.status_code, "length:", len(response.text))

    soup = BeautifulSoup(response.text, "lxml")
    links = soup.select("a[href*='/p/']")

    print("links found:", len(links))

    for link in links[:80]:
        product_url = link.get("href")
        text = link.get_text(" ", strip=True)

        if product_url and product_url.startswith("/"):
            product_url = "https://www.ikea.com" + product_url

        if product_url and text:
            rows.append({
                "category_url": category_url,
                "product_url": product_url,
                "raw_text": text
            })

    time.sleep(2)

seen = set()
clean_rows = []

for row in rows:
    if row["product_url"] not in seen:
        seen.add(row["product_url"])
        clean_rows.append(row)

with open("ikea_final_raw.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["category_url", "product_url", "raw_text"]
    )
    writer.writeheader()
    writer.writerows(clean_rows)

print("saved", len(clean_rows), "products")
