import os
from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from pathlib import Path

# --- Configuration ---
# This creates the DB file inside your 'data' folder
DB_PATH = Path("data/comments.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

Base = declarative_base()

# --- Table Definitions ---

class Video(Base):
    """Stores metadata about the YouTube Video itself."""
    __tablename__ = 'videos'
    
    video_id = Column(String, primary_key=True)
    title = Column(String)
    channel_name = Column(String)
    scanned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship: One Video has Many Comments
    comments = relationship("Comment", back_populates="video", cascade="all, delete-orphan")

class Comment(Base):
    """Stores individual comments."""
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String, ForeignKey('videos.video_id'))
    
    author = Column(String)
    text = Column(Text)
    # --- MAKE SURE THIS LINE EXISTS ---
    cleaned_text = Column(Text, nullable=True) 
    # ----------------------------------
    likes = Column(Integer)
    published_at = Column(String)
    sentiment_score = Column(Integer, nullable=True)
    sentiment_label = Column(String, nullable=True)
    cluster_id = Column(Integer, nullable=True)
    video = relationship("Video", back_populates="comments")

# --- Database Operations ---

class DBManager:
    def __init__(self, db_url=DATABASE_URL):
        # Ensure data directory exists
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        
    def init_db(self):
        """Creates the tables if they don't exist."""
        Base.metadata.create_all(self.engine)
        print(f"✅ Database initialized at {DB_PATH}")

    def save_comments(self, video_id, comments_data):
        """
        Saves a list of comment dictionaries to the DB.
        """
        session = self.Session()
        try:
            # 1. Ensure Video Record Exists
            # (In a real app, you'd fetch the video title via API too. 
            # For now, we use a placeholder or check if it exists)
            video = session.query(Video).filter_by(video_id=video_id).first()
            if not video:
                video = Video(video_id=video_id, title="Unknown Title", channel_name="Unknown Channel")
                session.add(video)
            
            # Update scan time
            video.scanned_at = datetime.utcnow()
            
            # 2. Add Comments
            # We assume comments_data is the list of dicts from your scraper
            count = 0
            for c in comments_data:
                # Deduplication check (optional but recommended): 
                # Check if same author+text exists for this video? 
                # For speed/simplicity now, we just insert.
                
                new_comment = Comment(
                    video_id=video_id,
                    author=c['author'],
                    text=c['text'],
                    likes=c['likes'],
                    published_at=c['published_at']
                )
                session.add(new_comment)
                count += 1
            
            session.commit()
            print(f"💾 Saved {count} comments to database.")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Database Error: {e}")
        finally:
            session.close()

if __name__ == "__main__":
    # Test the initialization
    db = DBManager()
    db.init_db()