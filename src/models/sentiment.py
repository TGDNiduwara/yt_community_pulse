import sys
from pathlib import Path
from transformers import pipeline
from tqdm import tqdm # Progress bar

# --- Fix Path for Imports ---
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.db.manager import DBManager, Comment

def analyze_sentiment():
    print("--- 🧠 Loading AI Model (this may take a moment) ---")
    
    # 1. Load the Pipeline
    # We use a specific model optimized for English text classification
    # It downloads automatically on the first run.
    sentiment_pipeline = pipeline(
        "sentiment-analysis", 
        model="distilbert-base-uncased-finetuned-sst-2-english",
        device=-1 # Set to 0 if you have a GPU and PyTorch with CUDA, else -1 for CPU
    )
    
    # 2. Connect to DB
    db = DBManager()
    session = db.Session()
    
    try:
        # Fetch comments that have CLEAN text but NO sentiment label yet
        comments = session.query(Comment).filter(
            Comment.cleaned_text != None,
            Comment.sentiment_label == None
        ).all()
        
        print(f"🔍 Found {len(comments)} comments to analyze.")
        if not comments:
            return

        # 3. Batch Processing
        # processing one by one is fine for < 1000 comments
        for comment in tqdm(comments, desc="Analyzing"):
            # The model fails on empty strings, so skip them
            if not comment.cleaned_text.strip():
                comment.sentiment_label = "NEUTRAL"
                comment.sentiment_score = 0
                continue
                
            # Run Inference
            # Returns a list like: [{'label': 'POSITIVE', 'score': 0.99}]
            result = sentiment_pipeline(comment.cleaned_text[:512]) # Truncate to 512 tokens max
            
            label = result[0]['label']
            score = result[0]['score']
            
            # Update Record
            comment.sentiment_label = label
            # Convert float (0.98) to Integer (98) for your DB Schema
            comment.sentiment_score = int(score * 100)

        session.commit()
        print(f"✅ AI Analysis complete! Database updated.")
        
    except Exception as e:
        print(f"❌ Error during inference: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    analyze_sentiment()