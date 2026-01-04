import sys
from pathlib import Path
from transformers import pipeline
from tqdm import tqdm # Progress bar

# --- Fix Path for Imports ---
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.db.manager import DBManager, Comment

def analyze_sentiment(batch_size=32):
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

        # 3. Batch Processing for efficiency (10x faster than one-by-one)
        texts_to_analyze = []
        comment_objects = []
        
        for comment in comments:
            # The model fails on empty strings, so mark them as NEUTRAL
            if not comment.cleaned_text.strip():
                comment.sentiment_label = "NEUTRAL"
                comment.sentiment_score = 0
            else:
                texts_to_analyze.append(comment.cleaned_text[:512])
                comment_objects.append(comment)
        
        # Process in batches if we have comments to analyze
        if texts_to_analyze:
            for i in tqdm(range(0, len(texts_to_analyze), batch_size), desc="Analyzing batches"):
                batch_texts = texts_to_analyze[i:i + batch_size]
                batch_comments = comment_objects[i:i + batch_size]
                
                # Run batch inference (much faster than one-by-one)
                results = sentiment_pipeline(batch_texts)
                
                # Update records with batch results
                for comment, result in zip(batch_comments, results):
                    comment.sentiment_label = result['label']
                    comment.sentiment_score = int(result['score'] * 100)

        session.commit()
        print(f"✅ AI Analysis complete! Database updated.")
        
    except Exception as e:
        print(f"❌ Error during inference: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    analyze_sentiment()