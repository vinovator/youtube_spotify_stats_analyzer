# app.py
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="YouTube & Spotify Analyzer", layout="wide")

# -----------------------
# Helpers
# -----------------------
def now_ts():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def timestamped_filename(prefix):
    return f"{prefix}_{now_ts()}.csv"

def sanitize_filename(s: str) -> str:
    return s.replace(" ", "_").replace(":", "-")

def extract_datetime_from_filename(filename: str) -> str:
    name = filename
    if name.lower().endswith(".csv"):
        name = name[:-4]
    parts = name.split("_")
    if len(parts) >= 3:
        date_part = parts[-2]
        time_part = parts[-1]
        return f"{date_part} {time_part.replace('-', ':')}"
    return "Unknown Date"

# -----------------------
# Load credentials
# -----------------------
# YouTube key (single-line file)
try:
    with open("google_api_key.txt", "r", encoding="utf-8") as f:
        youtube_api_key = f.read().strip()
except Exception:
    youtube_api_key = ""
    st.warning("google_api_key.txt not found or unreadable. Put your YouTube API key in that file.")

# Spotify credentials (CLIENT_ID=..., CLIENT_SECRET=...)
spotify_client_id = ""
spotify_client_secret = ""
try:
    with open("spotify_credentials.txt", "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                if k.strip().upper() == "CLIENT_ID":
                    spotify_client_id = v.strip()
                elif k.strip().upper() == "CLIENT_SECRET":
                    spotify_client_secret = v.strip()
except Exception:
    spotify_client_id = ""
    spotify_client_secret = ""
    st.warning("spotify_credentials.txt not found or unreadable. Create it with CLIENT_ID=... and CLIENT_SECRET=...")

# -----------------------
# YouTube helpers
# -----------------------
YOUTUBE_CATEGORIES = {
    "1": "Film & Animation", "2": "Autos & Vehicles", "10": "Music", "15": "Pets & Animals",
    "17": "Sports", "18": "Short Movies", "19": "Travel & Events", "20": "Gaming",
    "21": "Videoblogging", "22": "People & Blogs", "23": "Comedy", "24": "Entertainment",
    "25": "News & Politics", "26": "Howto & Style", "27": "Education",
    "28": "Science & Technology", "29": "Nonprofits & Activism", "30": "Movies",
    "31": "Anime/Animation", "32": "Action/Adventure", "33": "Classics", "34": "Comedy",
    "35": "Documentary", "36": "Drama", "37": "Family", "38": "Foreign", "39": "Horror",
    "40": "Sci-Fi/Fantasy", "41": "Thriller", "42": "Shorts", "43": "Shows", "44": "Trailers"
}

def extract_youtube_id(url: str) -> str:
    s = url.strip()
    if "v=" in s:
        return s.split("v=")[1].split("&")[0]
    if "youtu.be/" in s:
        return s.split("youtu.be/")[1].split("?")[0]
    return ""

def chunkify(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def fetch_youtube_videos(video_ids):
    results = {}
    if not youtube_api_key:
        return results
    base = "https://www.googleapis.com/youtube/v3/videos"
    for chunk in chunkify(video_ids, 50):  # batch 50 per request
        params = {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(chunk),
            "key": youtube_api_key
        }
        try:
            r = requests.get(base, params=params, timeout=20)
        except Exception as e:
            st.error(f"YouTube request error: {e}")
            continue
        if r.status_code != 200:
            st.error(f"YouTube API error {r.status_code}: {r.text}")
            continue
        data = r.json()
        for item in data.get("items", []):
            vid = item.get("id")
            if vid:
                results[vid] = item
    return results

def build_youtube_row(item, input_url):
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    content = item.get("contentDetails", {})
    cat = snippet.get("categoryId", "")
    return {
        "Title": snippet.get("title"),
        "URL": input_url,
        "Video ID": item.get("id"),
        "Published Date": snippet.get("publishedAt"),
        "Channel Name": snippet.get("channelTitle"),
        "Tags": ", ".join(snippet.get("tags", [])),
        "Category ID": cat,
        "Category Name": YOUTUBE_CATEGORIES.get(cat, "Unknown"),
        "Duration": content.get("duration", ""),
        "Views": stats.get("viewCount", ""),
        "Likes": stats.get("likeCount", "Not available"),
        "Comments": stats.get("commentCount", "Not available"),
        "Reporting Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# -----------------------
# Spotify helpers (requests-only)
# -----------------------
def extract_spotify_id(s: str) -> str:
    s = s.strip()
    if s.startswith("spotify:track:"):
        return s.split("spotify:track:")[1].split(":")[0]
    if "open.spotify.com/track/" in s:
        return s.split("open.spotify.com/track/")[1].split("?")[0]
    # maybe user pasted just an id or a url with query removed
    if len(s) >= 8 and all(c.isalnum() or c in "-_" for c in s):
        return s
    return ""

def get_spotify_token(client_id: str, client_secret: str) -> str:
    if not client_id or not client_secret:
        return ""
    url = "https://accounts.spotify.com/api/token"
    try:
        resp = requests.post(url, data={"grant_type": "client_credentials"}, auth=(client_id, client_secret), timeout=10)
    except Exception:
        return ""
    if resp.status_code != 200:
        return ""
    return resp.json().get("access_token", "")

def search_spotify_track(query: str, token: str):
    # returns top track item or None
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "limit": 1}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
    except Exception:
        return None
    if r.status_code != 200:
        return None
    data = r.json()
    items = data.get("tracks", {}).get("items", [])
    return items[0] if items else None

def fetch_spotify_track_details(track_id: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(f"https://api.spotify.com/v1/tracks/{track_id}", headers=headers, timeout=10)
    except Exception as e:
        return None, f"Request error: {e}"
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}: {r.text}"
    t = r.json()

    # audio features (tempo, danceability, energy)
    features = {}
    try:
        fresp = requests.get(f"https://api.spotify.com/v1/audio-features/{track_id}", headers=headers, timeout=10)
        if fresp.status_code == 200:
            features = fresp.json()
    except Exception:
        features = {}

    # artist followers (first artist)
    artist_followers = None
    try:
        if t.get("artists"):
            artist_id = t["artists"][0].get("id")
            if artist_id:
                ar = requests.get(f"https://api.spotify.com/v1/artists/{artist_id}", headers=headers, timeout=10)
                if ar.status_code == 200:
                    artist_followers = ar.json().get("followers", {}).get("total")
    except Exception:
        artist_followers = None

    artists = ", ".join([a.get("name") for a in t.get("artists", []) if a.get("name")])
    return {
        "Track Name": t.get("name"),
        "Track URL": t.get("external_urls", {}).get("spotify", f"https://open.spotify.com/track/{track_id}"),
        "Artists": artists,
        "Album": t.get("album", {}).get("name"),
        "Release Date": t.get("album", {}).get("release_date"),
        "Duration (ms)": t.get("duration_ms"),
        "Popularity": t.get("popularity"),
        "Artist Followers": artist_followers,
        "Tempo": features.get("tempo"),
        "Danceability": features.get("danceability"),
        "Energy": features.get("energy"),
        "Reporting Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }, None

# -----------------------
# UI: Tabs
# -----------------------
st.title("📊 Media Stats Analyzer — YouTube & Spotify")
tab_yt, tab_sp = st.tabs(["YouTube", "Spotify"])

# ---- YouTube tab ----
with tab_yt:
    st.header("📺 YouTube Video Analyzer")
    st.info("Paste multiple YouTube URLs (one per line). Example: https://www.youtube.com/watch?v=VIDEO_ID or https://youtu.be/VIDEO_ID")
    yt_input = st.text_area("YouTube URLs (one per line)", height=200, placeholder="https://www.youtube.com/watch?v=...")
    if st.button("Analyze YouTube Videos", key="analyze_yt"):
        if not yt_input.strip():
            st.error("Please enter at least one YouTube URL.")
        elif not youtube_api_key:
            st.error("YouTube API key missing. Add your key to google_api_key.txt.")
        else:
            lines = [l.strip() for l in yt_input.splitlines() if l.strip()]
            ids = []
            url_map = {}
            for l in lines:
                vid = extract_youtube_id(l)
                if not vid:
                    st.warning(f"Could not parse video id from: {l}")
                    continue
                ids.append(vid)
                url_map[vid] = l
            if not ids:
                st.error("No valid YouTube IDs parsed.")
            else:
                items_map = fetch_youtube_videos(ids)
                rows = []
                for vid in ids:
                    item = items_map.get(vid)
                    if not item:
                        st.warning(f"No data returned for video id: {vid} (input: {url_map.get(vid)})")
                        continue
                    row = build_youtube_row(item, url_map.get(vid))
                    rows.append(row)
                if rows:
                    df_yt = pd.DataFrame(rows)
                    st.subheader("📋 Video Data Table")
                    st.dataframe(df_yt, use_container_width=True)
                    csv_bytes = df_yt.to_csv(index=False).encode("utf-8")
                    fname = timestamped_filename("youtube_analysis")
                    st.download_button("📥 Download CSV", data=csv_bytes, file_name=fname, mime="text/csv")
                else:
                    st.warning("No valid video data found.")

    st.markdown("---")
    st.subheader("📊 Compare Two YouTube Data Snapshots")
    st.write("Upload two CSVs downloaded from this app (filenames must include the timestamp).")
    f1 = st.file_uploader("Upload First CSV (older)", type=["csv"], key="yt_f1")
    f2 = st.file_uploader("Upload Second CSV (newer)", type=["csv"], key="yt_f2")
    if f1 and f2:
        try:
            df1 = pd.read_csv(f1)
            df2 = pd.read_csv(f2)
        except Exception as e:
            st.error(f"Error reading CSVs: {e}")
        else:
            d1 = extract_datetime_from_filename(f1.name)
            d2 = extract_datetime_from_filename(f2.name)
            st.write(f"Snapshot 1: **{d1}**  →  Snapshot 2: **{d2}**")
            if "URL" not in df1.columns or "URL" not in df2.columns:
                st.error("Both CSVs must contain 'URL' column to compare.")
            else:
                merged = pd.merge(df1, df2, on="URL", suffixes=("_old", "_new"))
                for col in ["Views", "Likes", "Comments"]:
                    oldc = f"{col}_old"
                    newc = f"{col}_new"
                    if oldc in merged.columns and newc in merged.columns:
                        merged[oldc] = pd.to_numeric(merged[oldc], errors="coerce").fillna(0)
                        merged[newc] = pd.to_numeric(merged[newc], errors="coerce").fillna(0)
                        merged[f"{col} Change"] = merged[newc] - merged[oldc]
                display_cols = [c for c in [
                    "Title_old", "URL",
                    "Views_old", "Views_new", "Views Change",
                    "Likes_old", "Likes_new", "Likes Change",
                    "Comments_old", "Comments_new", "Comments Change"
                ] if c in merged.columns]
                change_df = merged[display_cols].rename(columns={"Title_old": "Title"})
                st.subheader("📈 Changes between snapshots")
                st.dataframe(change_df, use_container_width=True)
                change_csv = change_df.to_csv(index=False).encode("utf-8")
                fname = f"youtube_changes_{sanitize_filename(d1)}_to_{sanitize_filename(d2)}.csv"
                st.download_button("📥 Download Changes CSV", data=change_csv, file_name=fname, mime="text/csv")

# ---- Spotify tab ----
with tab_sp:
    st.header("🎧 Spotify Track Analyzer")
    st.info("You can either paste Spotify track URLs/URIs (one per line) OR paste track titles (one per line) and the app will search Spotify for the top match.")
    input_mode = st.radio("Input mode", ["Track URLs/URIs", "Track Titles (search)"], index=0)
    sp_input = st.text_area("Enter items (one per line)", height=200, placeholder="Either spotify URLs/URIs or titles like 'Blinding Lights - The Weeknd'")

    if st.button("Analyze Spotify Tracks", key="analyze_sp"):
        if not sp_input.strip():
            st.error("Please enter at least one line.")
        elif not spotify_client_id or not spotify_client_secret:
            st.error("Spotify credentials missing. Add CLIENT_ID and CLIENT_SECRET to spotify_credentials.txt.")
        else:
            token = get_spotify_token(spotify_client_id, spotify_client_secret)
            if not token:
                st.error("Could not obtain Spotify access token. Check CLIENT_ID/CLIENT_SECRET.")
            else:
                lines = [l.strip() for l in sp_input.splitlines() if l.strip()]
                rows = []
                for l in lines:
                    if input_mode == "Track URLs/URIs":
                        tid = extract_spotify_id(l)
                        if not tid:
                            st.warning(f"Could not extract track id from: {l}")
                            continue
                        st.write(f"🔍 Extracted track ID: `{tid}`")
                        data, err = fetch_spotify_track_details(tid, token)
                        if err:
                            st.warning(f"{l} -> {err}")
                            continue
                        # ensure Track URL column contains original input if external url missing
                        if not data.get("Track URL"):
                            data["Track URL"] = l
                        rows.append(data)
                    else:  # Track Titles
                        # search for title
                        st.write(f"🔎 Searching for: `{l}`")
                        item = search_spotify_track(l, token)
                        if not item:
                            st.warning(f"No match found for title: {l}")
                            continue
                        tid = item.get("id")
                        if not tid:
                            st.warning(f"No track id for search result: {l}")
                            continue
                        st.write(f"✔ Top match: `{item.get('name')}` by {', '.join([a.get('name') for a in item.get('artists', [])])}")
                        data, err = fetch_spotify_track_details(tid, token)
                        if err:
                            st.warning(f"{l} -> {err}")
                            continue
                        rows.append(data)

                if rows:
                    df_sp = pd.DataFrame(rows)
                    st.subheader("📋 Track Data Table")
                    st.dataframe(df_sp, use_container_width=True)
                    csv_bytes = df_sp.to_csv(index=False).encode("utf-8")
                    fname = timestamped_filename("spotify_analysis")
                    st.download_button("📥 Download CSV", data=csv_bytes, file_name=fname, mime="text/csv")
                else:
                    st.warning("No valid track data found.")

    st.markdown("---")
    st.subheader("📊 Compare Two Spotify Data Snapshots")
    st.write("Upload two CSVs downloaded from this app and the app will compute changes in Popularity and Artist Followers when available.")
    s1 = st.file_uploader("Upload First CSV (older)", type=["csv"], key="sp_f1")
    s2 = st.file_uploader("Upload Second CSV (newer)", type=["csv"], key="sp_f2")
    if s1 and s2:
        try:
            df1 = pd.read_csv(s1)
            df2 = pd.read_csv(s2)
        except Exception as e:
            st.error(f"Error reading CSVs: {e}")
        else:
            d1 = extract_datetime_from_filename(s1.name)
            d2 = extract_datetime_from_filename(s2.name)
            st.write(f"Snapshot 1: **{d1}**  →  Snapshot 2: **{d2}**")
            # prefer Track URL, fallback to Track Name
            merge_key = None
            if "Track URL" in df1.columns and "Track URL" in df2.columns:
                merge_key = "Track URL"
            elif "Track Name" in df1.columns and "Track Name" in df2.columns:
                merge_key = "Track Name"
            else:
                st.error("CSV files must contain 'Track URL' or 'Track Name' columns to compare.")
            if merge_key:
                merged = pd.merge(df1, df2, on=merge_key, suffixes=("_old", "_new"))
                for col in ["Popularity", "Artist Followers"]:
                    oldc = f"{col}_old"
                    newc = f"{col}_new"
                    if oldc in merged.columns and newc in merged.columns:
                        merged[oldc] = pd.to_numeric(merged[oldc], errors="coerce").fillna(0)
                        merged[newc] = pd.to_numeric(merged[newc], errors="coerce").fillna(0)
                        merged[f"{col} Change"] = merged[newc] - merged[oldc]
                display_cols = []
                if "Track Name_old" in merged.columns:
                    display_cols.append("Track Name_old")
                display_cols.append(merge_key)
                for col in ["Popularity", "Artist Followers"]:
                    for c in (f"{col}_old", f"{col}_new", f"{col} Change"):
                        if c in merged.columns:
                            display_cols.append(c)
                display_cols = [c for c in display_cols if c in merged.columns]
                change_df = merged[display_cols].rename(columns={"Track Name_old": "Track Name"})
                st.subheader("📈 Changes between snapshots")
                st.dataframe(change_df, use_container_width=True)
                change_csv = change_df.to_csv(index=False).encode("utf-8")
                fname = f"spotify_changes_{sanitize_filename(d1)}_to_{sanitize_filename(d2)}.csv"
                st.download_button("📥 Download Changes CSV", data=change_csv, file_name=fname, mime="text/csv")

st.markdown("---")
st.info("Keep credential files out of version control (add to .gitignore): google_api_key.txt, spotify_credentials.txt")
