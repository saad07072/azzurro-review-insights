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
    print("\n=======================================================")
    print("  🏨 Azzurro Hotels - Operations Review Dashboard")
    print("  🚀 Server running at: http://127.0.0.1:8000")
    print("  📖 API Documentation: http://127.0.0.1:8000/docs")
    print("=======================================================\n")
    uvicorn.run("app.api:app", host="127.0.0.1", port=8000, reload=False)
