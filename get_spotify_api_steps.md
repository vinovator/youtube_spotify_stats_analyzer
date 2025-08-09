# How to get Spotify API credentials (step-by-step)

This file explains, step-by-step, how to create Spotify API credentials (Client ID & Client Secret) and how to store them so the Streamlit app can use them via the **Client Credentials Flow** (suitable for public, non-user-specific data such as track metadata and audio features).

---

## 1) Create a Spotify developer account

1. Open: [https://developer.spotify.com/dashboard/](https://developer.spotify.com/dashboard/)
2. Log in with your regular Spotify account (or create one if you don’t have one).
3. You will land on the **Dashboard**.

## 2) Create an app and get Client ID / Client Secret

1. Click **Create an App** (or the **Create** button).
2. Give it a name (e.g. `youtube-spotify-analyzer`) and an optional description.
3. Click **Create**.
4. On the app page you’ll now see **Client ID** and a button/link to reveal the **Client Secret**. Copy both values.

> **Note:** Keep these values private. Do not commit them to a public Git repository.

## 3) Decide which flow you need

- **Client Credentials Flow**: Use this if you only need public, non-user-specific data (track metadata, audio features, artist info, album data). This is what the Streamlit app uses.
- **Authorization Code Flow (OAuth)**: Required if you need user-specific data (e.g., a user’s saved tracks, playlists, or follower actions). That requires redirect URIs and extra steps.

For the app in this repo we’ll use **Client Credentials Flow** — no redirect URI required.

## 4) Save credentials locally (recommended method for this app)

Create a file in your project folder named `spotify_credentials.txt` with either of these two supported formats:

**Option A — key=value format** (recommended):

```
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
```

**Option B — two-line format** (simple):

```
your_client_id_here
your_client_secret_here
```

Make sure to add `spotify_credentials.txt` to your `.gitignore` so it isn’t committed.

`.gitignore` example:

```
# local credentials
api_key.txt
spotify_credentials.txt
```

## 5) Install Python package `spotipy`

The app uses `spotipy`, a lightweight Python wrapper for the Spotify Web API.

Install it with:

```bash
pip install spotipy
```

Or add it to your `requirements.txt`:

```
spotipy
```

## 6) Quick test script (Client Credentials Flow)

Create a file `spotify_test.py` with this content (replace placeholder values if you don’t use `spotify_credentials.txt`):

```python
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = Spotify(auth_manager=auth_manager)

# test: fetch track metadata and audio features for a known track
track_id = "3n3Ppam7vgaVa1iaRUc9Lp"  # example track id
track = sp.track(track_id)
features = sp.audio_features([track_id])[0]

print("Track:", track['name'])
print("Artists:", [a['name'] for a in track['artists']])
print("Popularity:", track['popularity'])
print("Duration (ms):", track['duration_ms'])
print("Tempo:", features['tempo'])
```

Run it:

```
python spotify_test.py
```

If it prints track information, your credentials are working.

## 7) Using environment variables (alternative)

If you prefer not to store a text file, you can export environment variables on your machine:

Linux / macOS:

```bash
export SPOTIPY_CLIENT_ID="your_client_id"
export SPOTIPY_CLIENT_SECRET="your_client_secret"
```

Windows (PowerShell):

```powershell
$env:SPOTIPY_CLIENT_ID = "your_client_id"
$env:SPOTIPY_CLIENT_SECRET = "your_client_secret"
```

`spotipy` automatically reads these environment variables when present.

## 8) Notes & troubleshooting

- If you get `401` errors: double-check your Client ID / Client Secret and confirm the app hasn’t been deleted from the dashboard.
- If you need user-specific endpoints (e.g., user playlists, saved tracks), you'll need to implement the Authorization Code Flow and set redirect URIs in the Spotify dashboard. This app does not require that.
- Rate limiting: Spotify enforces API rate limits; if you plan to analyze thousands of tracks quickly, you may receive 429 responses. Implement backoff or limit batch size.

---

That’s it — once you have `spotify_credentials.txt` in the project folder (or set environment variables), the Streamlit app’s Spotify tab will read credentials automatically and let you analyze tracks, download CSV snapshots, and compare two snapshots for changes.

---

*End of instructions.*

