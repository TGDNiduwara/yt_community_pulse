import os
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from src.db.manager import DBManager

# Load environment variables (API Key)
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_video_comments(video_id, max_comments=200):
    """
    Fetches comments and replies for a specific video.
    
    Args:
        video_id (str): The 11-character YouTube Video ID.
        max_comments (int): Safety limit to prevent quota drain.
    
    Returns:
        list: A list of dictionaries containing comment data.
    """
    if not API_KEY:
        print("❌ Error: YOUTUBE_API_KEY not found in .env")
        return []

    # 1. Initialize Client
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    comments_data = []
    next_page_token = None
    quota_used = 0
    
    print(f"--- 📡 Connecting to YouTube API for Video: {video_id} ---")

    try:
        while len(comments_data) < max_comments:
            # 2. Make the Request
            # 'textFormat': 'plainText' removes some HTML (<b>) automatically
            request = youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=100,  # Max allowed by API per page
                textFormat="plainText",
                pageToken=next_page_token
            )
            
            response = request.execute()
            quota_used += 1  # 1 Request = roughly 1 Unit cost for this endpoint
            
            # 3. Process the Page
            for item in response.get('items', []):
                # Extract Top Level Comment
                top_comment = item['snippet']['topLevelComment']['snippet']
                comments_data.append({
                    'author': top_comment['authorDisplayName'],
                    'text': top_comment['textDisplay'],
                    'likes': top_comment['likeCount'],
                    'published_at': top_comment['publishedAt'],
                    'type': 'top_level'
                })
                
                # Extract Replies (if they exist in this packet)
                if 'replies' in item:
                    for reply in item['replies']['comments']:
                        reply_snip = reply['snippet']
                        comments_data.append({
                            'author': reply_snip['authorDisplayName'],
                            'text': reply_snip['textDisplay'],
                            'likes': reply_snip['likeCount'],
                            'published_at': reply_snip['publishedAt'],
                            'type': 'reply'
                        })
            
            print(f"   Fetched {len(comments_data)} comments so far... (Quota used: ~{quota_used} units)")

            # 4. Handle Pagination
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break  # No more comments
                
    except HttpError as e:
        print(f"❌ API Error: {e}")
        if e.resp.status == 403:
            print("   (This usually means Quota Exceeded or API not enabled)")

    print(f"--- ✅ Done! Collected {len(comments_data)} total comments. ---")
    return comments_data

if __name__ == "__main__":
    TEST_VIDEO_ID = "kqtD5dpn9C8" 
    if len(sys.argv) > 1:
        TEST_VIDEO_ID = sys.argv[1]

    # 1. Fetch
    results = get_video_comments(TEST_VIDEO_ID, max_comments=150)
    
    # 2. Save
    if results:
        print("--- 💾 Saving to Database ---")
        db = DBManager()
        db.init_db() # Ensure tables exist
        db.save_comments(TEST_VIDEO_ID, results)