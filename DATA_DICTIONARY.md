# Data Dictionary

The application expects a local CSV catalog at `data/movies.csv`.

## Required fields

| Column | Type | Description |
|---|---|---|
| `title` | string | Movie title shown to the user. |
| `year` | integer | Release year of the film. |
| `genres` | string | Pipe-delimited genres, for example `Drama|Thriller`. |
| `language` | string | Original or primary language label. Can be `Unknown` when unavailable. |
| `industry` | string | Source industry, for example `Hollywood` or `Bollywood`. |
| `runtime_minutes` | integer | Runtime in minutes. |
| `vote_average` | float | IMDb-style or demo rating score. |
| `vote_count` | integer | Number of ratings or votes. |
| `overview` | string | Summary description used in textual matching and UI output. |

## Notes
- Empty values are tolerated and normalized to safe defaults.
- Duplicate movie records are removed using the title/year pair or a stable `movieId` when present.
- The demo dataset is a curated prototype catalog and should not be treated as a production-grade metadata source.
- If an external movie metadata provider is added later, it should store its own licensing notices and credentials separately.
