import re
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "STAT418 student project - educational use"
}

raw = pd.read_csv("ikea_final_raw.csv")

rows = []

for i, row in raw.iterrows():
    url = row["product_url"]
    category_url = row["category_url"]

    print("scraping", i + 1, url)

    try:
        response = requests.get(url, headers=headers, timeout=20)
        text = BeautifulSoup(response.text, "lxml").get_text(" ", strip=True)

        slug = url.rstrip("/").split("/")[-1]
        name = re.sub(r"-[0-9]+$", "", slug).replace("-", " ").title()

        price = None
        rating = None
        review_count = None

        price_match = re.search(r"Price \$\s*([0-9]+(?:\.[0-9]{2})?)", text)
        if price_match:
            price = float(price_match.group(1))

        rating_match = re.search(r"Review:\s*([0-9.]+)\s*out of 5 stars", text)
        if rating_match:
            rating = float(rating_match.group(1))

        review_match = re.search(r"Total reviews:\s*([0-9,]+)", text)
        if review_match:
            review_count = int(review_match.group(1).replace(",", ""))

        rows.append({
            "category_url": category_url,
            "product_url": url,
            "name": name,
            "price": price,
            "rating": rating,
            "review_count": review_count,
            "page_text_length": len(text.split())
        })

    except Exception as e:
        print("failed:", url, e)

    time.sleep(1)

df = pd.DataFrame(rows)
df.to_csv("ikea_product_pages.csv", index=False)

print("saved rows:", len(df))
print("products with price:", df["price"].notna().sum())
print("products with rating:", df["rating"].notna().sum())
print("products with review_count:", df["review_count"].notna().sum())
