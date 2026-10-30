# MovieMind — Personalized Movie Recommendation Engine

MovieMind is a runnable local prototype for movie discovery. Enter a natural-language description of what you want to watch and optionally filter by language, industry, genre, release year, runtime, and minimum rating. It ranks a local movie catalog and returns recommendations with explanations.

## What it does

- Natural-language content matching with TF-IDF (scikit-learn)
- Cosine similarity ranking
- Optional structured filters
- Top 5–10 recommendations
- Streamlit interface
- Basic like/dislike/save interactions (session-only)
- Local dataset; no API key or model download needed
- Tests for core recommendation behavior

## Important limitations

- The included catalog is a **small demonstration dataset** with manually assembled descriptions and approximate metadata. It is for software demonstration and learning, not a verified commercial movie database.
- The `match_percent` is a scaled TF-IDF cosine similarity score, **not** a probability that you will like a movie.
- The prototype does not train a neural network. TF-IDF plus cosine similarity is a standard content-based information-retrieval baseline and a useful first ML/NLP system.
- Feedback is only stored for the current Streamlit session; persistent user profiles are not implemented.
- Poster images and streaming links are not included. You can add them later through a licensed API such as TMDB, following its current terms and attribution requirements.
- Metadata and ratings should be verified against a trusted source before public release.

## Requirements

- Python 3.10 or newer recommended
- VS Code
- Internet connection only for installing Python packages; the app itself works locally after installation

## Run on Windows (PowerShell)

1. Extract the ZIP file.
2. Open the extracted `MovieMind` folder in VS Code.
3. Open Terminal → New Terminal.
4. Create a virtual environment:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, run this in Command Prompt instead:

   ```bat
   .venv\Scripts\activate.bat
   ```

5. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

6. Start the application:

   ```bash
   streamlit run app.py
   ```

7. Streamlit will show a local URL, usually `http://localhost:8501`. Open it in your browser.

## Optional: build a saved TF-IDF artifact

```bash
python build_model.py
```

The app builds and caches the model representation automatically, so this step is optional.

## Run tests

```bash
python -m pytest -q
```

## Project structure

```text
MovieMind/
├── app.py
├── recommender.py
├── build_model.py
├── requirements.txt
├── README.md
├── data/
│   └── movies.csv
├── artifacts/
└── tests/
    └── test_recommender.py
```

## How recommendations work

1. Each movie's title, genres, language, industry, and overview are combined into a text document.
2. TF-IDF converts these documents into weighted word and phrase vectors.
3. The user's description is vectorized with the same vocabulary.
4. Cosine similarity ranks movies by text relevance.
5. Structured filters remove ineligible results.
6. A small rating-based tie-breaker is applied to the ranking.
7. The app shows the top results and a transparent metadata-based explanation.

## Recommended next improvements

1. Replace the demo CSV with a properly licensed, larger and verified catalog.
2. Add a semantic embedding backend such as `sentence-transformers/all-MiniLM-L6-v2`, then evaluate it against this baseline.
3. Create a labeled test set of user queries and relevant movies; evaluate Precision@10, Recall@10, and NDCG@10.
4. Add persistent feedback storage and a user preference profile.
5. Add posters and availability using an appropriately licensed movie API.
6. Add deduplication and diversity-aware ranking.

## CSV schema

`data/movies.csv` includes:
- `title`
- `year`
- `genres` (pipe-separated)
- `language`
- `industry`
- `runtime_minutes`
- `vote_average`
- `vote_count`
- `overview`

You can add more rows as long as these columns remain available.

## Deployment readiness

- `PROJECT_AUDIT.md` contains the project review and findings.
- `DATA_DICTIONARY.md` documents the dataset schema.
- `DEPLOYMENT.md` explains local, GitHub, and Streamlit Cloud setup.
- `FINAL_DEPLOYMENT_REPORT.md` summarizes the final verification and test status.

## Security notes

- Keep `.env` and `.streamlit/secrets.toml` out of version control.
- Use Streamlit Cloud secrets for any future external APIs.
- Do not commit local virtual environments or generated temporary files.
