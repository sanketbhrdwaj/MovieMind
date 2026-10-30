# Project Audit

## Scope reviewed
- `app.py`
- `recommender.py`
- `build_model.py`
- `merge_movielens.py`
- `requirements.txt`
- `README.md`
- `data/`
- `tests/`
- `.gitignore`

## Summary
MovieMind is a small Streamlit-based recommendation prototype built around a TF-IDF + cosine similarity search. The core app works for a curated local catalog and the recommender logic is intentionally simple and lightweight for deployment in a modest environment.

## What is working
- Local CSV-based catalog loading works with the provided `data/movies.csv`.
- Streamlit UI renders a search box, filters, and recommendation cards.
- TF-IDF vectorization and cosine similarity provide a reasonable text-based ranking baseline.
- Basic session-scoped feedback and saved-movie interaction remains intact.
- The project includes a pytest suite for core recommendation behavior.

## Issues identified
1. Some catalog assumptions were brittle because the application expected exact columns and values without validation.
2. Genre filtering was too loose and could silently match unintended strings.
3. Empty or malformed records could cause avoidable runtime errors.
4. The repository had incomplete deployment and documentation configuration for GitHub and Streamlit Cloud.
5. `.gitignore` was not comprehensive enough for Python projects and secret management.
6. The app and Python modules needed stronger handling for missing metadata and invalid inputs.

## Architecture notes
- `app.py` is the Streamlit entry point.
- `recommender.py` contains data validation, TF-IDF building, and recommendation logic.
- `build_model.py` serializes the vectorizer/matrix for reuse, although the app also builds cached resources automatically.
- `merge_movielens.py` can augment the demo CSV with MovieLens metadata, but it should not be used for production-grade metadata unless the source is curated and licensed.

## Recommendations
- Keep the content-based approach as the default baseline.
- Add optional semantic embeddings later rather than making them mandatory.
- Use the provided demo CSV for local development and small deployments.
- Treat the app as an educational or prototype recommender unless a verified external metadata source is added.

## Security and deployment notes
- No secrets or API keys are required for the baseline local app.
- Avoid committing `.venv`, `.env`, or `streamlit/secrets.toml` files.
- For deployment, keep all credentials in Streamlit Cloud secrets rather than code.
