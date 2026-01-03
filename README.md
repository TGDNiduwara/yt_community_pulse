# 📺 YouTube Community Pulse

A full-stack NLP application that ingests YouTube comments, analyzes sentiment and topics using AI, and visualizes the "vibe" of a community in a real-time dashboard.

## 🏗 Architecture

The system follows a modular ETL (Extract, Transform, Load) & ML pipeline:

1.  **Ingestion (`src/ingest`)**:
    * Connects to YouTube Data API v3.
    * Handles pagination and quota management to fetch comments efficiently.
    * **Output**: Raw text stored in SQLite.

2.  **Processing (`src/processing`)**:
    * Cleans noise (HTML tags, emojis, spam links).
    * **Output**: Normalized text ready for ML.

3.  **Intelligence (`src/models`)**:
    * **Sentiment Analysis**: Uses HuggingFace Transformers (`distilbert-base-uncased`) to classify comments as POSITIVE or NEGATIVE.
    * **Topic Modeling**: Uses Scikit-Learn (TF-IDF + K-Means) to cluster comments into thematic groups automatically.

4.  **Visualization (`src/app`)**:
    * Interactive Plotly Dash application.
    * Displays sentiment distribution, topic clusters, and a searchable data table.

## 🚀 Installation

**Prerequisites**: Python 3.12+ and `uv` package manager.

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd yt_community_pulse
    ```

2.  **Install dependencies:**
    ```bash
    uv sync
    ```

3.  **Setup API Key:**
    * Get a key from [Google Cloud Console](https://console.cloud.google.com/).
    * Create a `.env` file in the root:
        ```ini
        YOUTUBE_API_KEY=AIzaSyD_YOUR_KEY_HERE
        ```

## 🛠 Usage

**1. Fetch Comments**
Download comments for a specific video (e.g., Mosh's Python tutorial):
```bash
uv run src/ingest/fetch_comments.py kqtD5dpn9C8