import os
import uvicorn
import json
from app.config import SAMPLE_JSON_PATH
from app.database import init_db, get_all_reviews
from app.scraper import BookingReviewScraper

def bootstrap():
    init_db()
    scraper = BookingReviewScraper()
    sync_result = scraper.run_sync()
    print(f"Database initialized: {sync_result['new_reviews_added']} reviews added, {sync_result['duplicates_prevented']} duplicates skipped.")
    
    all_data = get_all_reviews()
    with open(SAMPLE_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    bootstrap()
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    print(f"Starting server on http://localhost:{port} (API docs: http://localhost:{port}/docs)")
    uvicorn.run("app.api:app", host=host, port=port, reload=False)
