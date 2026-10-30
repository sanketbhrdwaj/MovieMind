from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DEFAULT_DATA = Path(__file__).resolve().parent / "data" / "movies.csv"
DEFAULT_QUERY = "popular engaging movie with a compelling story"


def _clean_text(value: object) -> str:
    if value is None:
        return ""
    missing = pd.isna(value)
    if isinstance(missing, (bool, np.bool_)) and missing:
        return ""
    return str(value).strip()


def _normalize_text(value: object) -> str:
    return " ".join(_clean_text(value).split()).lower()


def _normalize_genre(value: object) -> str:
    return _normalize_text(_clean_text(value).replace("_", " ").replace("-", " "))


def _genre_tokens(value: object) -> list[str]:
    tokens = []
    for part in _clean_text(value).split("|"):
        cleaned = _normalize_genre(part)
        if cleaned:
            tokens.append(cleaned)
    return tokens


def _require_columns(df: pd.DataFrame, required: set[str]) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Movie dataset is missing columns: {missing}")


def load_movies(path: str | Path = DEFAULT_DATA) -> pd.DataFrame:
    """Load and validate the local movie catalog."""
    data_path = Path(path)
    if not data_path.exists():
        raise FileNotFoundError(f"Movie catalog not found at: {data_path}")

    try:
        df = pd.read_csv(data_path)
    except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError) as exc:  # pragma: no cover - defensive
        raise ValueError(f"Unable to parse movie dataset: {data_path}") from exc

    if df.empty:
        raise ValueError("The movie dataset contains no rows.")

    column_aliases = {
        "description": "overview",
        "plot": "overview",
        "movie_id": "movieId",
        "id": "movieId",
    }
    df = df.rename(columns=column_aliases)
    required = {
        "title", "year", "genres", "language", "industry",
        "runtime_minutes", "vote_average", "vote_count", "overview"
    }
    _require_columns(df, required)

    df = df.dropna(subset=["title"]).copy()
    df["title"] = df["title"].map(_clean_text)
    df = df[df["title"] != ""].copy()

    for col in ["year", "runtime_minutes", "vote_average", "vote_count"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["genres", "language", "industry", "overview"]:
        df[col] = df[col].fillna("").astype(str)

    df["genres"] = df["genres"].apply(lambda value: "|".join(
        part.strip() for part in str(value).split("|") if part.strip()
    ))
    df["language"] = df["language"].apply(lambda value: _clean_text(value) or "Unknown")
    df["industry"] = df["industry"].apply(lambda value: _clean_text(value) or "Unknown")
    df["overview"] = df["overview"].apply(lambda value: _clean_text(value))

    if "movieId" in df.columns:
        df["movieId"] = pd.to_numeric(df["movieId"], errors="coerce")

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["runtime_minutes"] = pd.to_numeric(df["runtime_minutes"], errors="coerce")
    df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce")
    df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce")

    df["genres"] = df["genres"].str.replace("||", "|", regex=False).str.strip("|")
    df["genre_tokens"] = df["genres"].apply(_genre_tokens)

    if "movieId" in df.columns:
        dedupe_key = ["movieId"]
    else:
        dedupe_key = ["title", "year"]

    df = df.drop_duplicates(subset=dedupe_key, keep="first").reset_index(drop=True)
    if df.empty:
        raise ValueError("The movie dataset contains no usable records.")
    return df


def _movie_document(row: pd.Series) -> str:
    """Create a text document for content-based retrieval."""
    return " ".join([
        str(row.get("title", "")),
        str(row.get("genres", "")).replace("|", " "),
        str(row.get("language", "")),
        str(row.get("industry", "")),
        str(row.get("overview", "")),
    ]).strip()


class MovieRecommender:
    """Content-based recommender using TF-IDF and cosine similarity."""

    def __init__(self, movies: pd.DataFrame):
        self.movies = movies.reset_index(drop=True).copy()
        if "genre_tokens" not in self.movies.columns:
            self.movies["genre_tokens"] = self.movies["genres"].apply(_genre_tokens)
        self.documents = self.movies.apply(_movie_document, axis=1).map(_clean_text).tolist()
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_features=50000,
            sublinear_tf=True,
        )
        self.matrix = self.vectorizer.fit_transform(self.documents)

    def recommend(
        self,
        query: str,
        n: int = 10,
        language: str | None = None,
        industry: str | None = None,
        genre: str | None = None,
        min_year: int | None = None,
        max_year: int | None = None,
        max_runtime: int | None = None,
        min_rating: float | None = None,
        exclude_titles: Iterable[str] | None = None,
    ) -> pd.DataFrame:
        """Return the highest-ranked movies matching the query and filters."""
        cleaned_query = _normalize_text(query)
        if not cleaned_query:
            cleaned_query = DEFAULT_QUERY

        try:
            limit = max(1, int(n))
        except (TypeError, ValueError):
            limit = 10
        limit = min(limit, 50)

        qvec = self.vectorizer.transform([cleaned_query])
        scores = cosine_similarity(qvec, self.matrix).ravel()
        results = self.movies.copy()
        results["match_score"] = scores

        if language and language != "Any":
            target = _normalize_text(language)
            results = results[results["language"].map(_normalize_text) == target]
        if industry and industry != "Any":
            target = _normalize_text(industry)
            results = results[results["industry"].map(_normalize_text) == target]
        if genre and genre != "Any":
            target = _normalize_genre(genre)
            results = results[results["genre_tokens"].apply(lambda tokens: target in set(tokens))]
        if min_year is not None:
            results = results[results["year"].fillna(0) >= min_year]
        if max_year is not None:
            results = results[results["year"].fillna(9999) <= max_year]
        if max_runtime is not None:
            results = results[results["runtime_minutes"].fillna(9999) <= max_runtime]
        if min_rating is not None:
            results = results[results["vote_average"].fillna(0) >= float(min_rating)]

        excluded = { _normalize_text(title) for title in exclude_titles or [] }
        if excluded:
            results = results[~results["title"].map(_normalize_text).isin(excluded)]

        if results.empty:
            return results.drop(columns=["genre_tokens"], errors="ignore").reset_index(drop=True)

        rating_signal = results["vote_average"].fillna(0).clip(lower=0, upper=10) / 10.0
        results["rating_signal"] = rating_signal
        results["genre_signal"] = results["genre_tokens"].apply(
            lambda tokens: 1.0 if (genre and genre != "Any" and _normalize_genre(genre) in set(tokens)) else 0.0
        )
        results["ranking_score"] = 0.82 * results["match_score"] + 0.08 * results["genre_signal"] + 0.10 * results["rating_signal"]
        results = results.sort_values(["ranking_score", "vote_count", "vote_average"], ascending=[False, False, False])
        results = results.drop_duplicates(subset=["title"], keep="first").head(limit)
        results["match_percent"] = (results["match_score"].clip(0, 1) * 100).round(1)
        results["reason"] = results.apply(lambda row: self._explain(cleaned_query, row), axis=1)
        return results.drop(columns=["genre_tokens"], errors="ignore").reset_index(drop=True)

    @staticmethod
    def _explain(query: str, row: pd.Series) -> str:
        parts: list[str] = []
        if row.get("genres"):
            parts.append(f"genres: {row['genres']}")
        if row.get("language"):
            parts.append(f"language: {row['language']}")
        overview = _clean_text(row.get("overview"))
        if overview:
            parts.append(overview)
        if not parts:
            return f"Matched using your description: {query}"
        return "Matched using your description and movie metadata: " + "; ".join(parts[:3])


def build_recommender(path: str | Path = DEFAULT_DATA) -> MovieRecommender:
    return MovieRecommender(load_movies(path))
