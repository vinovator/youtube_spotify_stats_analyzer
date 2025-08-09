## **README.md**

````markdown
# 📊 YouTube Video Analyzer & Snapshot Comparator

A Streamlit web app that allows you to:
1. **Analyze multiple YouTube videos** by providing their URLs.
2. **Download a CSV report** of video stats including title, views, likes, comments, tags, duration, and more.
3. **Compare two CSV snapshots** to see changes in views, likes, and comments over time.

---

## 🚀 Features
- Fetches **video metadata** from the YouTube Data API.
- Reads **API key** securely from a local `api_key.txt` file.
- Supports both **youtube.com/watch?v=** and **youtu.be/** link formats.
- Shows results in an **interactive Streamlit table**.
- Downloads CSV files with **timestamped filenames**.
- Uploads two previously saved CSV reports to **compare** changes.
- Displays **delta metrics** for views, likes, and comments.

---

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/vinovator/youtube_stats_analyzer.git
   cd youtube_stats_analyzer
````

2. **Create a virtual environment** (optional but recommended)

   ```bash
   python -m venv venv
   source venv/bin/activate   # Mac/Linux
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create `api_key.txt`**

   * Go to [Google Cloud Console](https://console.cloud.google.com/)
   * Enable the **YouTube Data API v3**
   * Create an API key and save it in `api_key.txt` in the project folder.

   Example `api_key.txt`:

   ```
   YOUR_YOUTUBE_API_KEY_HERE
   ```

---

## ▶️ Running the App

Run:

```bash
streamlit run app.py
```

Replace `app.py` with your script name.

---

## 📂 CSV File Naming Convention

CSV reports are saved with a timestamp:

```
youtube_analysis_YYYY-MM-DD_HH-MM-SS.csv
```

The comparator uses this timestamp in filenames to determine when the snapshots were taken.

---

## 📊 Example Output

### **Analyzer Table**

| Title      | Views | Likes | Comments | Duration | Category Name |
| ---------- | ----: | ----: | -------: | -------- | ------------- |
| Sample Vid |  1200 |   150 |       12 | PT5M30S  | Music         |

### **Comparison Table**

| Title      | Views Old | Views New | Views Change | Likes Old | Likes New | Likes Change | Comments Old | Comments New | Comments Change |
| ---------- | --------: | --------: | -----------: | --------: | --------: | -----------: | -----------: | -----------: | --------------: |
| Sample Vid |      1200 |      1500 |          300 |       150 |       160 |           10 |           12 |           15 |               3 |

---

## 🛠 Requirements

* Python 3.8+
* YouTube Data API key

---

## ⚠️ Notes

* API calls are subject to **YouTube Data API v3 quota limits**.
* Keep your `api_key.txt` safe and **never commit it to public repositories**.
* If your quota is exceeded, you’ll need to wait for reset or use a different API key.

---

## 📜 License

MIT License

---

**Author:** HVS

````

---
