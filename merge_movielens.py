
from pathlib import Path
import re

import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
SOURCE = DATA / "movielens"

movies_file = SOURCE / "movies.csv"
ratings_file = SOURCE / "ratings.csv"
existing_file = DATA / "movies.csv"

if not movies_file.exists() or not ratings_file.exists():
    raise FileNotFoundError(
        "Place MovieLens movies.csv and ratings.csv "
        "inside data/movielens/"
    )

# Load MovieLens data
movies = pd.read_csv(movies_file)
ratings = pd.read_csv(ratings_file)

# Calculate average user rating and number of ratings
rating_stats = ratings.groupby("movieId").agg(
    vote_average=("rating", "mean"),
    vote_count=("rating", "count"),
).reset_index()

movies = movies.merge(rating_stats, on="movieId", how="left")

# Extract year from titles such as Toy Story (1995)
def extract_year(title):
    match = re.search(r"\((\d{4})\)\s*$", str(title))
    return int(match.group(1)) if match else None

movies["year"] = movies["title"].apply(extract_year)

# Convert MovieLens columns to MovieMind schema
new_movies = pd.DataFrame({
    "title": movies["title"].str.replace(
        r"\s*\(\d{4}\)\s*$", "", regex=True
    ).str.strip(),
    "year": movies["year"],
    "genres": movies["genres"],
    "language": "Unknown",
    "industry": "Unknown",
    "runtime_minutes": None,
    "vote_average": movies["vote_average"],
    "vote_count": movies["vote_count"],
    "overview": "",
})

new_movies["vote_average"] = new_movies["vote_average"].fillna(0)
new_movies["vote_count"] = new_movies["vote_count"].fillna(0)

# Preserve the original curated demo records
if existing_file.exists():
    existing = pd.read_csv(existing_file)
    combined = pd.concat(
        [existing, new_movies],
        ignore_index=True
    )
else:
    combined = new_movies

# Remove duplicate title/year records
combined["title"] = combined["title"].astype(str).str.strip()
combined = combined.drop_duplicates(
    subset=["title", "year"],
    keep="first"
)

combined.to_csv(existing_file, index=False)

print("MovieMind catalog updated!")
print(f"MovieLens records imported: {len(new_movies)}")
print(f"Total unique catalog entries: {len(combined)}")
print(f"Saved to: {existing_file}")
print("\nSample records:")
print(combined[["title", "year", "genres"]].head(10))
