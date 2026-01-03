import sys
from pathlib import Path
import re
import html

# --- Fix Path for Imports ---
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.db.manager import DBManager, Comment

def clean_text(text: str) -> str:
    """
    Removes HTML tags, decodes entities, and normalizes whitespace.
    """
    if not text:
        return ""
        
    # 1. Decode HTML entities (e.g., "&quot;" -> '"')
    text = html.unescape(text)
    
    # 2. Remove HTML tags (e.g., "<b>Hi</b>" -> "Hi")
    # This regex looks for anything between < and >
    text = re.sub(r'<[^>]+>', '', text)
    
    # 3. Remove Links (Basic Spam Filter)
    text = re.sub(r'http\S+|www.\S+', '[LINK_REMOVED]', text)
    
    # 4. Normalize Whitespace (replace tabs/newlines with single space)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def run_cleaning_pipeline():
    print("--- 🧹 Starting Text Cleaning Pipeline ---")
    db = DBManager()
    session = db.Session()
    
    try:
        # Get all comments that haven't been cleaned yet
        comments = session.query(Comment).filter(Comment.cleaned_text == None).all()
        print(f"Found {len(comments)} comments to clean.")
        
        for c in comments:
            original = c.text
            cleaned = clean_text(original)
            
            # Update the record
            c.cleaned_text = cleaned
            
            # Optional: Print diff if they are different
            if original != cleaned and len(original) < 50:
               print(f"   [Dirty]: {original}\n   [Clean]: {cleaned}")

        session.commit()
        print(f"✅ Successfully cleaned {len(comments)} comments.")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    # Mini-Test to verify logic immediately
    test_str = "Hello <b>World!</b> &amp; check this: http://spam.com"
    print(f"Test Input:  {test_str}")
    print(f"Test Output: {clean_text(test_str)}")
    print("-" * 30)
    
    # Run the real pipeline
    run_cleaning_pipeline()