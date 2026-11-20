import sqlite3
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_hash TEXT UNIQUE NOT NULL,
            property_id TEXT NOT NULL,
            property_name TEXT NOT NULL,
            reviewer_name TEXT,
            reviewer_country TEXT,
            review_date TEXT NOT NULL,
            rating REAL NOT NULL,
            title TEXT,
            positive_text TEXT,
            negative_text TEXT,
            full_text TEXT NOT NULL,
            room_type TEXT,
            stay_duration TEXT,
            topics TEXT,
            sentiment TEXT,
            scraped_at TEXT NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_property_date ON reviews(property_id, review_date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rating ON reviews(rating);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentiment ON reviews(sentiment);")
    conn.commit()
    conn.close()

def generate_review_hash(property_id: str, reviewer_name: str, review_date: str, full_text: str) -> str:
    raw = f"{property_id}_{reviewer_name or 'anon'}_{review_date}_{full_text[:100]}".strip().lower()
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def insert_review(review_data: Dict[str, Any]) -> bool:
    """Inserts a review. Returns True if inserted, False if already exists (duplicate avoided)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    review_hash = review_data.get("review_hash") or generate_review_hash(
        review_data["property_id"],
        review_data.get("reviewer_name", ""),
        review_data["review_date"],
        review_data["full_text"]
    )
    
    topics_json = json.dumps(review_data.get("topics", [])) if isinstance(review_data.get("topics"), list) else review_data.get("topics", "[]")
    scraped_at = review_data.get("scraped_at") or datetime.utcnow().isoformat()
    
    try:
        cursor.execute("""
            INSERT INTO reviews (
                review_hash, property_id, property_name, reviewer_name, reviewer_country,
                review_date, rating, title, positive_text, negative_text, full_text,
                room_type, stay_duration, topics, sentiment, scraped_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            review_hash,
            review_data["property_id"],
            review_data["property_name"],
            review_data.get("reviewer_name", "Anonymous"),
            review_data.get("reviewer_country", "Australia"),
            review_data["review_date"],
            float(review_data["rating"]),
            review_data.get("title", ""),
            review_data.get("positive_text", ""),
            review_data.get("negative_text", ""),
            review_data["full_text"],
            review_data.get("room_type", "Standard Room"),
            review_data.get("stay_duration", "1 night"),
            topics_json,
            review_data.get("sentiment", "neutral"),
            scraped_at
        ))
        conn.commit()
        inserted = True
    except sqlite3.IntegrityError:
        inserted = False
    finally:
        conn.close()
    return inserted

def query_reviews(
    property_id: Optional[str] = None,
    sentiment: Optional[str] = None,
    topic: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search_query: Optional[str] = None,
    limit: int = 200,
    offset: int = 0
) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    
    conditions = []
    params = []
    
    if property_id and property_id != "all":
        conditions.append("property_id = ?")
        params.append(property_id)
    if sentiment and sentiment != "all":
        conditions.append("sentiment = ?")
        params.append(sentiment)
    if topic and topic != "all":
        conditions.append("topics LIKE ?")
        params.append(f'%"{topic}"%')
    if start_date:
        conditions.append("review_date >= ?")
        params.append(start_date)
    if end_date:
        conditions.append("review_date <= ?")
        params.append(end_date)
    if search_query:
        conditions.append("(full_text LIKE ? OR title LIKE ?)")
        params.append(f"%{search_query}%")
        params.append(f"%{search_query}%")
        
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"""
        SELECT * FROM reviews 
        {where_clause} 
        ORDER BY review_date DESC 
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    
    results = []
    for row in rows:
        item = dict(row)
        try:
            item["topics"] = json.loads(item["topics"]) if item["topics"] else []
        except:
            item["topics"] = []
        results.append(item)
        
    conn.close()
    return results

def get_all_reviews() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reviews ORDER BY review_date DESC")
    rows = cursor.fetchall()
    results = []
    for row in rows:
        item = dict(row)
        try:
            item["topics"] = json.loads(item["topics"]) if item["topics"] else []
        except:
            item["topics"] = []
        results.append(item)
    conn.close()
    return results

def get_review_count() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM reviews")
    count = cursor.fetchone()[0]
    conn.close()
    return count
