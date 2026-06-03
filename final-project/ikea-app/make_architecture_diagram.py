import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

steps = [
    ("IKEA Website", "Product category pages + product detail pages"),
    ("Web Scraper", "requests + BeautifulSoup"),
    ("Raw Dataset", "398 product URLs"),
    ("Product Page Parser", "price, rating, review_count"),
    ("Clean Dataset", "398 products, 10 categories"),
    ("Feature Engineering", "category, price, rating, page text length"),
    ("ML Model", "Random Forest classifier"),
    ("Streamlit App", "Product Launch Advisor")
]

fig, ax = plt.subplots(figsize=(12, 7))
ax.axis("off")

x = 0.5
y_start = 0.92
y_gap = 0.105

for i, (title, subtitle) in enumerate(steps):
    y = y_start - i * y_gap

    box = FancyBboxPatch(
        (0.18, y - 0.045),
        0.64,
        0.07,
        boxstyle="round,pad=0.02",
        linewidth=1.5,
        edgecolor="black",
        facecolor="white"
    )
    ax.add_patch(box)

    ax.text(
        x,
        y,
        title,
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold"
    )

    ax.text(
        x,
        y - 0.028,
        subtitle,
        ha="center",
        va="center",
        fontsize=10
    )

    if i < len(steps) - 1:
        ax.annotate(
            "",
            xy=(x, y - 0.07),
            xytext=(x, y - 0.045),
            arrowprops=dict(arrowstyle="->", linewidth=1.5)
        )

plt.title("Solution Architecture and Data Flow", fontsize=18, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig("architecture_diagram.png", dpi=200)
plt.close()

print("saved architecture_diagram.png")
