import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ast
import io
import sys

buffer = io.StringIO()
sys.stdout = buffer

# load in data
base = os.path.abspath(os.path.join(os.path.dirname(__file__)))
filepath_csv = os.path.join(base, "data", "processed", "processed.csv")
df = pd.read_csv(filepath_csv)

# part 1: Rating Analysis

# part a: TMDB and Letterboxd rating correlation
rating_cor = round(df['rating'].corr(df['vote_average']), 4)
print(f"The correlation between TMDB and Letterboxd ratings is {rating_cor}.")
fig, ax = plt.subplots(figsize = (8,6))
sns.scatterplot(df, x = "rating", y = "vote_average", alpha = 0.6)
ax.set_xlabel("Letterboxd Rating")
ax.set_ylabel("TMDB Rating")
ax.set_title("TMDB Rating vs. Letterboxd Rating")
plt.tight_layout()
plt.show()

# part b: Distribution of ratings on each platform

# part 1: TMDB
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].hist(df['vote_average'], edgecolor="black")
axes[0].set_xlabel("TMDB rating")
axes[0].set_ylabel("Frequency")
axes[0].set_title("TMDB Rating Distribution (10pt scale)")

axes[1].hist(df['rating'], edgecolor="black")
axes[1].set_xlabel("Letterboxd Rating")
axes[1].set_ylabel("Frequency")
axes[1].set_title("Letterboxd Rating Distribution (5pt scale)")

plt.tight_layout()
plt.show()
print("The TMDB distribution has two missing values, but otherwise the distribution is roughly normal with a slight left skew and a center of 7 out of 10.")
print("The Letterboxd distribution is roughly normal with a center of about 3.25 out of 5.")
print(f"Thus, on the same scale, the two distributions are similar, but as we saw from the correlation, the relationship between the two scores is weak at {rating_cor}.")

# part 2: Genre Analysis

# part a: Most common genres
df['genres'] = df['genres'].apply(ast.literal_eval) # convert genres to lists
genres_exploded = df.explode("genres") # separate genres
# table
genre_counts = genres_exploded['genres'].value_counts() # count genre frequency
print(genre_counts)
# barplot
fig, ax = plt.subplots(figsize = (10,6))
sns.barplot(
    x = genre_counts.values,
    y = genre_counts.index,
    ax = ax,
    edgecolor = "black"
)
ax.set_xlabel("Genre")
ax.set_ylabel("Frequency")
ax.set_title("Most Frequent Genres")
plt.tight_layout()
plt.show()
print(genre_counts.index[1])
print(f"The most common genres are {genre_counts.index[0]} and {genre_counts.index[1]} with {genre_counts.values[0]} movies in the genre.")
print(f"The top five most common genres are {genre_counts.index[0]}, {genre_counts.index[1]}, {genre_counts.index[2]}, {genre_counts.index[3]}, and {genre_counts.index[4]}.")
print(f"The most uncommon genres are {genre_counts.index[-1]}, {genre_counts.index[-2]}, {genre_counts.index[3]}, and {genre_counts.index[4]} with {genre_counts.values[-1]} movie in each genre.")

# part b: compute average rating by genre

# Letterboxd
genre_letter_rate = genres_exploded.groupby('genres')['rating'].mean().round(4).sort_values(ascending=False)
print(genre_letter_rate)
print(f"The top three genres based on Letterboxd rating are {genre_letter_rate.index[0]}, {genre_letter_rate.index[1]}, and {genre_letter_rate.index[2]}.")
print(f"The bottom three genres based on Letterboxd rating are {genre_letter_rate.index[-3]}, {genre_letter_rate.index[-4]}, and {genre_letter_rate.index[-5]}.")

# TMDB
genre_tmdb_rate = genres_exploded.groupby('genres')['vote_average'].mean().round(4).sort_values(ascending = False)
print(genre_tmdb_rate)
print(f"The top three genres based on TMDB rating are {genre_tmdb_rate.index[0]}, {genre_tmdb_rate.index[1]}, and {genre_tmdb_rate.index[2]}.")
print(f"The bottom three genres based on TMDB rating are {genre_tmdb_rate.index[-1]}, {genre_tmdb_rate.index[-2]}, and {genre_tmdb_rate.index[-3]}.")
print("The two ratings had many similarities and differences.  The top genres both included science fiction and music movies, while the bottom genres both included horror movies.")
print("On the other hand, the top genres in Letterboxd included animation where TMDB included family movies.  Additionally, the bottom genres in Letterboxd had TV movie and romance where TMDB had documentary and fantasy.")

# part 3: Financial Analysis

# part a: Budget vs Revenue correlation
budget_rev_cor = round(df['budget'].corr(df['revenue']), 4)
print(f"The correlation between budget and revenue is {budget_rev_cor}, which is fairly strong indicating higher budget movies tend to have higher revenue.")
fig, ax = plt.subplots(figsize = (8,6))
sns.scatterplot(df, x = "budget", y = "revenue", alpha = 0.6)
ax.set_xlabel("Budget(\$10,000,000)")
ax.set_ylabel("Revenue(\$1,000,000,000)")
ax.set_title("Budget(\$10,000,000) vs Revenue(\$1,000,000,000)")
plt.tight_layout()
plt.show()

# part b: most profitable movies
df['profit'] = df['revenue'] - df['budget']
cols = ['title', 'profit']
movies_by_profit = df[cols].sort_values(by = "profit", ascending = False)
print(movies_by_profit.head(5))
top5_titles = movies_by_profit.head(5)["title"].tolist()
print(f"The most profitable movie is {top5_titles[0]} with a profit of ${movies_by_profit.head(1)["profit"].tolist()[0]}.")
print(f"The five most profitable movies are {top5_titles[0]}, {top5_titles[1]}, {top5_titles[2]}, {top5_titles[3]}, and {top5_titles[4]}.")

print("The data collection process struggled with foreign movies, so all movie titles are the English transaltions.")
print("Additionally, many movies had missing features that could not be filled mased on the information we had for example, number of fans.")
print("Future improvements would do anomaly analysis and try to fill rest of the missing values.")


sys.stdout = sys.__stdout__

# Write captured output to REPORT.md
report_path = os.path.join(base, "REPORT.md")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("# Movie Dataset Analysis Report\n\n")
    f.write("```\n")
    f.write(buffer.getvalue())
    f.write("\n```")




