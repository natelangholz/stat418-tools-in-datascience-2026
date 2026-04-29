import os
import json
from collections import defaultdict
import csv


# part 1: load data from both sources
# api data
base = os.path.abspath(os.path.join(os.path.dirname(__file__)))
filepath_api = os.path.join(base, "data", "raw", "tmdb", "media_data.json")
filepath_scrape = os.path.join(base, "data", "raw", "letterboxd", "letterboxd_movie_data.json")
with open(filepath_api, "r", encoding="utf-8") as f:
    api_data = json.load(f) 
with open(filepath_scrape, "r", encoding="utf-8") as f:
    scrape_data = json.load(f) 

# part 2: merge data on common identifiers(id)
merged = defaultdict(dict)
for item in api_data + scrape_data:
    merged[item['id']].update(item)


# part 3: cleans and validates data

# part a: validates data
all_keys = 0
for movie in merged.values():
    if len(movie.keys()) == 21: # all true => all keys exist for all moves
        all_keys += 1
print(f"{all_keys} movies have all 21 keys.")

missing = 0
for movie in merged.values():
    for attr in movie.values():
        if attr in (None, "", "NA"):
            missing += 1
print(f"There are {missing} None, \"\", or NA values in the movies dictionary.") 

for movie in merged.values():
    title = movie.get("title", "<no title>")
    for key, value in movie.items():
        if value in (None, "", "NA"):
            print(f"Missing value in movie '{title}' → field '{key}' = {value}")
print("Data is unavailable for these fields.")

# part 5: standardizes formats

# part a: dates
print("release_date values are string objects and not datetime because dictionaries do not support datetime objects.")

# part b: ratings
print("rating values are floats, and missing values are NoneType.")


# part 6: removes duplicates
def freeze(value):
    if isinstance(value, dict):
        return(tuple(sorted((k, freeze(v)) for k,v in value.items())))
    if isinstance(value, list):
        return tuple(freeze(v) for v in value)
    return value

unique = {}
seen = set()
for movie_id, movie in merged.items():
    frozen = freeze(movie)
    if frozen not in seen:
        seen.add(frozen)
        unique[movie_id] = movie

print("Unique count: ", len(unique))

# part 7: saves processed data as CSV and JSON

# part a: to json
os.makedirs("data/processed", exist_ok=True)
with open("data/processed/processed.json", "w", encoding="utf-8") as f:
    json.dump(merged, f, indent=2, ensure_ascii=False)

# part b: to csv
def flatten_value(v):
    if isinstance(v, list):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list): # dict in dict
        return json.dumps(v, ensure_ascii=False)
    return v
    

output_path = "data/processed/processed.csv"
fieldnames = set()
for movie in unique.values():
    fieldnames.update(movie.keys())
fieldnames = list(fieldnames)

with open(output_path, "w", encoding = "utf-8", newline = "") as f:
    writer = csv.DictWriter(f, fieldnames = fieldnames)
    writer.writeheader()

    for movie in unique.values():
        flat_row = {k: flatten_value(v) for k, v, in movie.items()}
        writer.writerow(flat_row)



