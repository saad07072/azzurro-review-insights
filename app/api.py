from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from typing import Optional
from app.config import BASE_DIR, PROPERTIES
from app.database import query_reviews, get_all_reviews, init_db, get_review_count
from app.nlp_insights import calculate_operations_metrics
from app.scraper import BookingReviewScraper
from app.seed_data import generate_sample_reviews

app = FastAPI(
    title="Azzurro Hotels - Booking.com Review Insights API",
    description="Operations intelligence backend for Booking.com guest review collection and sentiment analysis.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()
    # Check if DB has reviews. If empty, bootstrap with realistic sample baseline
    if get_review_count() == 0:
        scraper = BookingReviewScraper()
        scraper.run_sync()

@app.get("/api/properties")
def get_properties():
    return PROPERTIES

@app.get("/api/metrics")
def get_metrics(property_id: Optional[str] = "all"):
    all_revs = get_all_reviews()
    if property_id and property_id != "all":
        all_revs = [r for r in all_revs if r["property_id"] == property_id]
    return calculate_operations_metrics(all_revs)

@app.get("/api/reviews")
def get_reviews(
    property_id: Optional[str] = "all",
    sentiment: Optional[str] = "all",
    topic: Optional[str] = "all",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    reviews = query_reviews(
        property_id=property_id,
        sentiment=sentiment,
        topic=topic,
        start_date=start_date,
        end_date=end_date,
        search_query=search,
        limit=limit,
        offset=offset
    )
    return {
        "count": len(reviews),
        "results": reviews
    }

@app.post("/api/scrape")
def trigger_scrape():
    scraper = BookingReviewScraper()
    result = scraper.run_sync()
    return result

@app.get("/api/export")
def export_dataset():
    all_revs = get_all_reviews()
    return JSONResponse(content=all_revs)

# Mount frontend
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
def serve_index():
    index_file = BASE_DIR / "static" / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Azzurro Hotels Review Insights Dashboard API is active. Open /docs for Swagger UI."}
