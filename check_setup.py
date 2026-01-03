import torch
import transformers
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

def main():
    print("--- 1. Checking Environment ---")
    load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")
    if api_key:
        print(f"✅ API Key found: {api_key[:5]}... (hidden)")
    else:
        print("❌ API Key NOT found in .env")

    print("\n--- 2. Checking NLP Stack ---")
    print(f"PyTorch Version: {torch.__version__}")
    print(f"Transformers Version: {transformers.__version__}")
    
    if torch.cuda.is_available():
        print(f"🚀 GPU Available: {torch.cuda.get_device_name(0)}")
    else:
        print("⚠️  Running on CPU (Standard for simple inference)")

    print("\n--- 3. Attempting YouTube Connection ---")
    try:
        if api_key:
            youtube = build('youtube', 'v3', developerKey=api_key)
            print("✅ YouTube Client initialized successfully")
        else:
            print("Skipping YouTube check (No key)")
    except Exception as e:
        print(f"❌ YouTube Connection Failed: {e}")

if __name__ == "__main__":
    main()