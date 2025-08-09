# YouTube & Spotify Stats Analyzer

A simple **Streamlit** app to fetch, snapshot and compare YouTube video stats and Spotify track stats.

- YouTube: paste multiple video URLs → fetch title, views, likes, comments, duration, tags, etc. → preview table → download CSV snapshot with timestamp → compare two snapshots to see changes.
- Spotify: either paste **track URLs/URIs** or **type track titles (search)** (you can include artist name for better accuracy) → fetch metadata + audio features → preview table → download CSV snapshot → compare two snapshots to see changes in popularity / artist followers.

<img title="a Extract stats from YouTube video links" alt="Alt text" src="/img/youtube_video_extract.png">

<img title="a Compare YouTube Videos" alt="Alt text" src="/img/compare_youtube_videos.png">

<img title="a Extract Spotify Tracks" alt="Alt text" src="/img/spotify_track_extract.png">

<img title="a Compare Spotify Tracks" alt="Alt text" src="/img/spotify_track_compare.png">

---

## Quick links

- Run the app: `streamlit run app.py`
- Requirements: `pip install -r requirements.txt`

---

## What’s in this repository (root)

```
.gitignore
app.py
config/google_api_key_dummy.txt
config/spotify_credentials_dummy.txt
secrets/google_api_key.txt
secrets/spotify_credentials.txt
docs/get_spotify_api_steps.md
notebooks/youtube_data_extractor.ipynb
README.md
requirements.txt
youtube_analysis.py
```

**Notes:**

- `config/*_dummy.txt` are example files showing the expected format for credentials. They contain placeholder values and are safe to keep in repo.
- Your real keys should be placed under the secrets folder and should **not** be committed. See *Setup* below.

---

## Features

- Fetch metadata for multiple YouTube videos (supports `youtube.com/watch?v=` and `youtu.be/` links).
- Batch YouTube requests to reduce quota pressure (50 IDs per request where applicable).
- Fetch Spotify track metadata and audio features using Client Credentials flow (no user OAuth required).
- Two input modes for Spotify: **Track URLs/URIs** or **Track Titles (search)**.
  - **UX tip:** When using *Track Titles (search)*, include the artist name (e.g. `Blinding Lights - The Weeknd`) to improve match accuracy.
- Preview results in an interactive Streamlit table before downloading.
- Download CSV snapshots with timestamped filenames: `youtube_analysis_YYYY-MM-DD_HH-MM-SS.csv` and `spotify_analysis_YYYY-MM-DD_HH-MM-SS.csv`.
- Upload two previously downloaded CSV snapshots and compare changes:
  - YouTube: `Views`, `Likes`, `Comments` deltas (merged on `URL`).
  - Spotify: `Popularity`, `Artist Followers` deltas (merged on `Track URL` or `Track Name`).
- Lightweight dependency set (`streamlit`, `pandas`, `requests`) — no heavy Spotify wrappers required.

---

## Setup (create your API credentials locally)

### 1) Install dependencies

```bash
python -m venv venv     # optional but recommended
source venv/bin/activate  # macOS / Linux
# venv\Scripts\activate  # Windows PowerShell
pip install -r requirements.txt
```

### 2) Create credential files (two options)

**A — simplest (copy dummy files and edit)**

```bash
cp config/google_api_key_dummy.txt google_api_key.txt
cp config/spotify_credentials_dummy.txt spotify_credentials.txt
```

Then edit the created files:

- `google_api_key.txt` — replace placeholder with your YouTube Data API v3 key (single line):

```
YOUR_YOUTUBE_API_KEY_HERE
```

- `spotify_credentials.txt` — put your Spotify app credentials in **KEY=VALUE** format:

```
CLIENT_ID=your_spotify_client_id
CLIENT_SECRET=your_spotify_client_secret
```

**B — alternative: use a ****\`\`**** folder (recommended for local dev)** Create a `secrets/` folder (add to `.gitignore`) and place the real key files there. If you do that, either copy them back to project root before running the app or adjust `app.py` to read from `secrets/`.

**Important:** Do not commit `google_api_key.txt` or `spotify_credentials.txt` to git. Add them to `.gitignore`.

### 3) Get credentials

- YouTube: create an API key in Google Cloud Console and enable **YouTube Data API v3**.
- Spotify: create an app at the Spotify Developer Dashboard and copy **Client ID** and **Client Secret**. See `docs/get_spotify_api_steps.md` for step-by-step instructions.

---

## Running the app

```bash
streamlit run app.py
```

Open the URL shown in your terminal (typically `http://localhost:8501`).

---

## How to use

### YouTube tab

1. Paste multiple YouTube URLs (one per line). Formats supported: `https://www.youtube.com/watch?v=...` and `https://youtu.be/...`.
2. Click **Analyze Videos**. The app will fetch metadata and show a table.
3. Download CSV: click **Download CSV**. The file name includes the timestamp, e.g. `youtube_analysis_2025-08-09_11-42-15.csv`.
4. To compare snapshots: go to **Compare Two YouTube Data Snapshots** → upload an older CSV and a newer CSV (the app uses the filename timestamp to label snapshots) → the app merges by `URL` and shows changes for `Views`, `Likes`, `Comments`.

**Notes:**

- If YouTube hides like counts or comments, those fields may show `Not available`.
- The app uses batched YouTube API calls for efficiency; if you analyze hundreds of videos you may need to watch your quota.

### Spotify tab

1. Choose `Input mode`: either **Track URLs/URIs** or **Track Titles (search)**.
2. If you choose **Track Titles (search)**: include artist name if possible (e.g. `Save Your Tears - The Weeknd`) — this improves search accuracy.
3. Paste one item per line and click **Analyze Spotify Tracks**.
4. The app will search (title mode) or fetch directly (URL mode), display a table and let you download a timestamped CSV (`spotify_analysis_YYYY-MM-DD_HH-MM-SS.csv`).
5. To compare snapshots: upload older and newer CSVs (the app merges on `Track URL` or `Track Name`) and it will compute `Popularity` and `Artist Followers` changes when available.

---

## CSV filename conventions

- Snapshot filenames created by the app include timestamps and are parsed by the comparator by splitting the filename (no regex):
  - `youtube_analysis_YYYY-MM-DD_HH-MM-SS.csv`
  - `spotify_analysis_YYYY-MM-DD_HH-MM-SS.csv`
- Change outputs are named like: `youtube_changes_{date1}_to_{date2}.csv` or `spotify_changes_{date1}_to_{date2}.csv`.

---

## Troubleshooting & tips

- **Missing/invalid credentials:** ensure `google_api_key.txt` and `spotify_credentials.txt` exist and contain valid values.
- **Spotify search returns wrong track:** include artist name in the title input for more precise matching, or use Track URL mode.
- **API rate limits / 429 responses:** the app does not implement aggressive backoff — if you hit rate limits, wait and retry or analyze in smaller batches.
- **CSV compare fails to merge:** ensure both CSVs were produced by this app (they contain `URL` for YouTube, and `Track URL` / `Track Name` for Spotify).

---

## Recommended folder structure (short)

```
root/
├─ app.py
├─ config/ (dummy creds)
├─ docs/
├─ notebooks/
├─ requirements.txt
├─ README.md
└─ secrets/ (gitignored; put real google_api_key.txt and spotify_credentials.txt here or copy to root)
```

---

## Security & privacy

- Keep credential files private and out of git. If you accidentally commit keys, rotate them immediately.
- CSV snapshots may contain private channel/track data — keep them safe.

---

## License

MIT

---
