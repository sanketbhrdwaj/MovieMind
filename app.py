from __future__ import annotations

import html
import logging

import pandas as pd
import streamlit as st

from recommender import DEFAULT_DATA, build_recommender, load_movies

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="MovieMind | Movie Discovery",
    page_icon="🎬",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; max-width: 1250px;}
    .hero {padding: 1.6rem 1.8rem; border-radius: 18px;
           background: linear-gradient(120deg, #172554, #312e81, #701a75);
           color: white; margin-bottom: 1.2rem;}
    .hero h1 {font-size: 2.7rem; margin-bottom: .35rem;}
    .hero p {font-size: 1.05rem; opacity: .92;}
    .movie-card {padding: 1rem; border: 1px solid rgba(128,128,128,.3);
                 border-radius: 14px; min-height: 230px; margin-bottom: .5rem;}
    .score {font-weight: 700; font-size: 1rem;}
    .muted {opacity: .75; font-size: .9rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_engine():
    return build_recommender(DEFAULT_DATA)


@st.cache_data
def get_catalog():
    return load_movies(DEFAULT_DATA)


try:
    movies = get_catalog()
    engine = get_engine()
except Exception as exc:  # pragma: no cover - app-level safety
    logger.exception("MovieMind failed to load its catalog.")
    st.error(f"Unable to load the movie catalog: {exc}")
    st.stop()

st.markdown(
    """
    <div class="hero">
      <h1>🎬 MovieMind</h1>
      <p>Tell us what you're in the mood for. Discover movies that match your taste.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("🎛️ Refine your search")
    languages = ["Any"] + sorted({str(value).strip() for value in movies["language"].dropna().unique() if str(value).strip()})
    industries = ["Any"] + sorted({str(value).strip() for value in movies["industry"].dropna().unique() if str(value).strip()})
    all_genres = sorted({g.strip() for item in movies["genres"].fillna("") for g in str(item).split("|") if g.strip()})
    genres = ["Any"] + all_genres
    language = st.selectbox("Language", languages)
    industry = st.selectbox("Industry", industries)
    genre = st.selectbox("Genre", genres)
    min_year = int(movies["year"].min()) if not movies.empty else 1900
    max_year = int(movies["year"].max()) if not movies.empty else 2025
    year_range = st.slider("Release year", min_year, max_year, (min_year, max_year))
    max_runtime = st.slider("Maximum runtime (minutes)", 60, 240, 240, step=5)
    min_rating = st.slider("Minimum IMDb-style rating", 0.0, 9.0, 0.0, step=0.5)
    result_count = st.slider("Number of recommendations", 5, 10, 10)
    if st.button("Reset filters", use_container_width=True):
        st.session_state.pop("last_results", None)
        st.session_state.pop("last_query", None)
        st.rerun()

st.subheader("What do you want to watch?")
st.caption("Describe the mood, story, themes, or movies you already like. Filters are optional.")
query = st.text_area(
    "Your interests",
    value="A mind-bending thriller with unexpected twists, a mysterious atmosphere, and an emotional story",
    height=110,
    placeholder="Example: a funny, uplifting Hindi movie about friendship and self-discovery",
    label_visibility="collapsed",
)
col1, col2 = st.columns([1, 5])
with col1:
    search = st.button("✨ Find movies", type="primary", use_container_width=True)
with col2:
    st.caption("Tip: describe the feeling you want, not just a genre.")

if search or "last_results" not in st.session_state:
    with st.spinner("Finding movies that match your mood..."):
        results = engine.recommend(
            query=query,
            n=result_count,
            language=language,
            industry=industry,
            genre=genre,
            min_year=year_range[0],
            max_year=year_range[1],
            max_runtime=max_runtime,
            min_rating=min_rating if min_rating > 0 else None,
        )
    st.session_state["last_results"] = results
    st.session_state["last_query"] = query

results = st.session_state.get("last_results")
if results is not None:
    st.markdown("### Your recommendations")
    if results.empty:
        st.warning("No movies matched all selected filters. Try broadening your filters.")
    else:
        st.caption(f"Showing {len(results)} matches for: “{st.session_state.get('last_query', '')}”")
        cols_per_row = 2
        for start in range(0, len(results), cols_per_row):
            cols = st.columns(cols_per_row)
            for col, (_, movie) in zip(cols, results.iloc[start:start + cols_per_row].iterrows()):
                with col:
                    year = int(movie["year"]) if pd.notna(movie["year"]) else "N/A"
                    runtime = int(movie["runtime_minutes"]) if pd.notna(movie["runtime_minutes"]) else "N/A"
                    rating = f"{movie['vote_average']:.1f}/10" if pd.notna(movie["vote_average"]) else "N/A"
                    title = html.escape(str(movie["title"]))
                    genres = html.escape(str(movie["genres"]).replace("|", " • "))
                    language_value = html.escape(str(movie["language"]))
                    industry_value = html.escape(str(movie["industry"]))
                    overview = html.escape(str(movie["overview"]))
                    st.markdown(
                        f"""
                        <div class="movie-card">
                          <div class="score">🎯 {movie['match_percent']:.1f}% text relevance</div>
                          <h3>{title} ({year})</h3>
                          <div class="muted">{genres} · {language_value} · {runtime} min</div>
                          <p>⭐ {rating} &nbsp; | &nbsp; {industry_value}</p>
                          <p>{overview}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    with st.expander("Why this recommendation?"):
                        st.write(movie["reason"])
                    feedback_key = f"feedback_{movie['title']}_{year}"
                    fb1, fb2, fb3 = st.columns(3)
                    with fb1:
                        if st.button("👍 Like", key=feedback_key + "_like"):
                            st.session_state.setdefault("feedback", {})[movie["title"]] = "like"
                            st.toast("Thanks! Feedback captured for this session.")
                    with fb2:
                        if st.button("👎 Dislike", key=feedback_key + "_dislike"):
                            st.session_state.setdefault("feedback", {})[movie["title"]] = "dislike"
                            st.toast("Feedback captured for this session.")
                    with fb3:
                        if st.button("🔖 Save", key=feedback_key + "_save"):
                            st.session_state.setdefault("saved", set()).add(movie["title"])
                            st.toast("Saved for this session.")

with st.expander("About this prototype"):
    st.write(
        "MovieMind is a local content-based recommendation prototype. It uses TF-IDF text features "
        "and cosine similarity, with structured filters and a small curated demo catalog. "
        "The displayed relevance percentage is a scaled similarity score, not a probability that "
        "you will enjoy the movie. Catalog metadata and ratings are illustrative and should be "
        "verified before public or commercial release."
    )
    st.write(f"Catalog size: {len(movies)} movies.")
    st.write("Feedback and saved titles are stored only for the current Streamlit session in this prototype.")
