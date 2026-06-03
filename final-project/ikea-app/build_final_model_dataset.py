import pandas as pd

df = pd.read_csv("ikea_product_pages.csv")

def get_category(url):
    if "bookcases" in url:
        return "bookcases"
    if "tables-desks" in url:
        return "tables_desks"
    if "sofas" in url:
        return "sofas"
    if "beds" in url:
        return "beds"
    if "chairs" in url:
        return "chairs"
    if "dressers" in url:
        return "dressers"
    if "tv-media" in url:
        return "tv_media"
    if "storage" in url:
        return "storage"
    if "cabinets" in url:
        return "cabinets"
    if "outdoor" in url:
        return "outdoor"
    return "other"

df["category"] = df["category_url"].apply(get_category)

df = df.dropna(subset=["price", "rating", "review_count"])
df = df.drop_duplicates(subset=["product_url"])

median_reviews = df["review_count"].median()
df["high_interest"] = (df["review_count"] > median_reviews).astype(int)

df["name_length"] = df["name"].fillna("").str.split().apply(len)

cols = [
    "name",
    "category",
    "price",
    "rating",
    "review_count",
    "name_length",
    "page_text_length",
    "high_interest",
    "product_url",
]

df[cols].to_csv("ikea_model_dataset.csv", index=False)

print("rows:", len(df))
print("median review count:", median_reviews)
print("class balance:")
print(df["high_interest"].value_counts())
print(df[["name", "category", "price", "rating", "review_count", "high_interest"]].head())
