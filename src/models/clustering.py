import sys
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import pandas as pd

# --- Fix Path for Imports ---
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.db.manager import DBManager, Comment

def extract_topics(n_clusters=5):
    print(f"--- 🧩 Starting Topic Clustering (k={n_clusters}) ---")
    
    db = DBManager()
    session = db.Session()
    
    try:
        # 1. Load Data
        # We only want comments that have CLEAN text (and ignore short garbage)
        comments = session.query(Comment).filter(Comment.cleaned_text != "").all()
        
        if len(comments) < n_clusters:
            print("❌ Not enough comments to cluster.")
            return

        print(f"📚 Loaded {len(comments)} comments.")
        
        # Extract just the text for Scikit-Learn
        corpus = [c.cleaned_text for c in comments]
        
        # 2. Vectorize (Convert Text -> Numbers)
        # max_df=0.9: Ignore words appearing in 90% of documents (too common, like "the")
        # min_df=2: Ignore words appearing in less than 2 documents (typos/noise)
        # stop_words='english': Remove "and", "is", "but"
        vectorizer = TfidfVectorizer(max_df=0.9, min_df=2, stop_words='english')
        X = vectorizer.fit_transform(corpus)
        
        print(f"🧮 Created vectors: {X.shape} (Rows, Features)")

        # 3. K-Means Clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        kmeans.fit(X)
        
        # 4. Save Cluster IDs back to DB
        # The labels_ array contains the cluster ID (0, 1, 2...) for each comment
        for i, comment in enumerate(comments):
            comment.cluster_id = int(kmeans.labels_[i])
            
        session.commit()
        print("💾 Saved cluster IDs to database.")

        # 5. Extract Themes (What are these clusters?)
        print("\n--- 🏷️  Identified Themes ---")
        order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
        terms = vectorizer.get_feature_names_out()
        
        for i in range(n_clusters):
            # Get top 5 words for this cluster
            top_terms = [terms[ind] for ind in order_centroids[i, :5]]
            print(f"Cluster {i}: {', '.join(top_terms)}")
            
            # Optional: Print a sample comment from this cluster
            sample = session.query(Comment).filter_by(cluster_id=i).first()
            if sample:
                print(f"   Sample: \"{sample.cleaned_text[:60]}...\"")
            print("-" * 20)

    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    extract_topics()