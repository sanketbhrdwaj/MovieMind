"""Build and inspect the local TF-IDF movie representation."""
from pathlib import Path

import joblib

from recommender import build_recommender, DEFAULT_DATA


def main() -> None:
    artifacts = Path(__file__).resolve().parent / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)

    engine = build_recommender(DEFAULT_DATA)
    artifact_path = artifacts / "moviemind_tfidf.joblib"
    joblib.dump(
        {
            "vectorizer": engine.vectorizer,
            "matrix": engine.matrix,
            "movies": engine.movies,
        },
        artifact_path,
    )
    print(f"Built TF-IDF catalog for {len(engine.movies)} movies.")
    print(f"Saved artifacts to: {artifact_path}")
    print("The Streamlit app also builds/caches the catalog automatically.")


if __name__ == "__main__":
    main()
