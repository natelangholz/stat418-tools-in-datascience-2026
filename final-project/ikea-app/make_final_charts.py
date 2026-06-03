import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("ikea_final_clean.csv")

# -------------------------
# Category Distribution
# -------------------------
plt.figure(figsize=(8, 5))

df["category"].value_counts().sort_values().plot(kind="barh")

plt.title("Product Count by Category")
plt.xlabel("Count")
plt.ylabel("Category")

plt.tight_layout()
plt.savefig("category_distribution_final.png")
plt.close()

# -------------------------
# Class Balance
# -------------------------
plt.figure(figsize=(5, 4))

df["high_interest"].value_counts().sort_index().plot(kind="bar")

plt.title("Class Balance")
plt.xlabel("high_interest")
plt.ylabel("Count")

plt.tight_layout()
plt.savefig("class_balance_final.png")
plt.close()

# -------------------------
# Description Length
# -------------------------
plt.figure(figsize=(7, 5))

df["description_length"].hist(bins=20)

plt.title("Description Length Distribution")
plt.xlabel("Word Count")
plt.ylabel("Frequency")

plt.tight_layout()
plt.savefig("description_length_final.png")
plt.close()

print("charts saved")
