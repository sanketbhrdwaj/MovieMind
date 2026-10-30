# Deployment Guide

## Local development

```powershell
cd MovieMind
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## GitHub setup
1. Create a new repository on GitHub.
2. Push the project folder to the repository.
3. Ensure `.gitignore` excludes `.venv`, `.env`, and secrets.
4. Keep the app entry point at the repository root: `app.py`.

## Streamlit Community Cloud
1. Open Streamlit Cloud and sign in with GitHub.
2. Choose the repository and branch.
3. Set the app file to `app.py`.
4. Add any required secrets under Streamlit Secrets.
5. Redeploy after code updates.

## Secrets
Use `st.secrets` or `.streamlit/secrets.toml` locally only. Do not commit secrets.

## Common issues
- Missing packages: verify `requirements.txt` is in the repository root.
- Wrong working directory: ensure the app file is truly `app.py` at the root.
- Broken data path: the app uses `data/movies.csv` relative to the project root.
- Streamlit startup failure: run `python -m streamlit run app.py` locally first.
