import os
import uvicorn
import json
from app.config import SAMPLE_JSON_PATH
from app.database import init_db, get_all_reviews
from app.scraper import BookingReviewScraper

def bootstrap():
    print("[INIT] Initializing Azzurro Hotels Review Database...")
    init_db()
    scraper = BookingReviewScraper()
    sync_result = scraper.run_sync()
    print(f"[SYNC] Synced review database: {sync_result}")
    
    # Save a static sample_reviews.json deliverable
    all_data = get_all_reviews()
    with open(SAMPLE_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    print(f"[EXPORT] Saved {len(all_data)} sample reviews to {SAMPLE_JSON_PATH}")

if __name__ == "__main__":
    bootstrap()
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    print("\n=======================================================")
    print("  🏨 Azzurro Hotels - Operations Review Dashboard")
    print(f"  🚀 Server running on port {port}")
    print(f"  📖 API Documentation: http://127.0.0.1:{port}/docs")
    print("=======================================================\n")
    uvicorn.run("app.api:app", host=host, port=port, reload=False)
