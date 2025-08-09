import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- Load API Key from file ---
with open("google_api_key.txt", "r") as f:
    youtube_api_key = f.read().strip()

# --- Category Mapping ---
categories = {
    "1": "Film & Animation", "2": "Autos & Vehicles", "10": "Music", "15": "Pets & Animals",
    "17": "Sports", "18": "Short Movies", "19": "Travel & Events", "20": "Gaming",
    "21": "Videoblogging", "22": "People & Blogs", "23": "Comedy", "24": "Entertainment",
    "25": "News & Politics", "26": "Howto & Style", "27": "Education",
    "28": "Science & Technology", "29": "Nonprofits & Activism", "30": "Movies",
    "31": "Anime/Animation", "32": "Action/Adventure", "33": "Classics", "34": "Comedy",
    "35": "Documentary", "36": "Drama", "37": "Family", "38": "Foreign", "39": "Horror",
    "40": "Sci-Fi/Fantasy", "41": "Thriller", "42": "Shorts", "43": "Shows", "44": "Trailers"
}

# Create timestamp string
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Create filename with timestamp
filename = f"youtube_analysis_{timestamp}.csv"


# --- Streamlit UI ---
st.title("📊 YouTube Video Analyzer")
st.write("Paste multiple YouTube video URLs (one per line). The API key is securely read from `api_key.txt`.")

urls_input = st.text_area("Enter YouTube URLs (one per line)")

if st.button("Analyze Videos"):
    if not urls_input.strip():
        st.error("Please enter at least one YouTube URL.")
    else:
        video_urls = [u.strip() for u in urls_input.split("\n") if u.strip()]
        video_list = []

        for video_url in video_urls:
            if "v=" in video_url:
                video_id = video_url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in video_url:
                video_id = video_url.split("youtu.be/")[1].split("?")[0]
            else:
                st.warning(f"Invalid URL format: {video_url}")
                continue

            st.write(f"🔍 Extracted video ID: `{video_id}`")

            video_info_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id={video_id}&key={youtube_api_key}"
            response = requests.get(video_info_url)
            data = response.json()

            if "items" in data and len(data["items"]) > 0:
                item = data["items"][0]
                snippet = item["snippet"]
                stats = item.get("statistics", {})
                content = item.get("contentDetails", {})

                video_dict = {
                    "Title": snippet["title"],
                    "URL": video_url,
                    "Published Date": snippet["publishedAt"],
                    "Channel Name": snippet["channelTitle"],
                    "Tags": ", ".join(snippet.get("tags", [])),
                    "Category ID": snippet.get("categoryId", "Unknown"),
                    "Category Name": categories.get(snippet.get("categoryId", ""), "Unknown"),
                    "Duration": content.get("duration", ""),
                    "Views": stats.get("viewCount", ""),
                    "Likes": stats.get("likeCount", "Not available"),
                    "Comments": stats.get("commentCount", "Not available"),
                    "Reporting Date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                video_list.append(video_dict)
            else:
                st.warning(f"No data found for URL: {video_url}")

        if video_list:
            df = pd.DataFrame(video_list)

            # Show data in table format
            st.subheader("📋 Video Data Table")
            st.dataframe(df)

            # CSV Export
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=filename,
                mime="text/csv"
            )
        else:
            st.warning("No valid video data found.")


st.markdown("---")

st.subheader("📊 Compare Two YouTube Data Snapshots")

# Upload two CSV files
file1 = st.file_uploader("Upload First CSV File", type=["csv"])
file2 = st.file_uploader("Upload Second CSV File", type=["csv"])

def extract_datetime_from_filename(filename):
    # Example: youtube_analysis_2025-08-09_11-42-15.csv
    parts = filename.replace(".csv", "").split("_")
    if len(parts) >= 3:
        date_part = parts[-2]  # 2025-08-09
        time_part = parts[-1]  # 11-42-15
        return f"{date_part} {time_part.replace('-', ':')}"
    return "Unknown Date"

if file1 and file2:
    # Read CSV files
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Get snapshot dates from filenames
    date1 = extract_datetime_from_filename(file1.name)
    date2 = extract_datetime_from_filename(file2.name)

    st.write(f"📅 First file date: **{date1}**")
    st.write(f"📅 Second file date: **{date2}**")

    # Merge on URL or Title (URL is safer)
    merged_df = pd.merge(df1, df2, on="URL", suffixes=("_old", "_new"))

    # Ensure numeric types
    for col in ["Views", "Likes", "Comments"]:
        merged_df[f"{col}_old"] = pd.to_numeric(merged_df[f"{col}_old"], errors="coerce").fillna(0)
        merged_df[f"{col}_new"] = pd.to_numeric(merged_df[f"{col}_new"], errors="coerce").fillna(0)

    # Calculate changes
    merged_df["Views Change"] = merged_df["Views_new"] - merged_df["Views_old"]
    merged_df["Likes Change"] = merged_df["Likes_new"] - merged_df["Likes_old"]
    merged_df["Comments Change"] = merged_df["Comments_new"] - merged_df["Comments_old"]

    # Select columns for display
    change_df = merged_df[[
        "Title_old", "URL", "Views_old", "Views_new", "Views Change",
        "Likes_old", "Likes_new", "Likes Change",
        "Comments_old", "Comments_new", "Comments Change"
    ]].rename(columns={"Title_old": "Title"})

    # Show results
    st.subheader("📈 Change in Metrics")
    st.dataframe(change_df)

    # CSV download of changes
    change_csv = change_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Changes CSV",
        data=change_csv,
        file_name=f"youtube_changes_{date1}_to_{date2}.csv",
        mime="text/csv"
    )
