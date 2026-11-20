# Azzurro Hotels - Booking.com Review Dashboard

A web dashboard built for Azzurro Hotels operations teams to track guest reviews across four Sydney properties, spot common complaints (cleanliness, noise, check-in, etc.), and monitor week-on-week ratings.

Live demo: https://azzurro-review-insights-uax3.onrender.com

---

## Monitored Properties

- **Olympic Hotel Paddington**: `https://www.booking.com/hotel/au/olympic-paddington.html`
- **Potts Point (Venus Potts Point Sydney)**: `https://www.booking.com/hotel/au/venus-potts-point-sydney.html`
- **Central Sydney (Venus Surry Hills)**: `https://www.booking.com/hotel/au/venus-surry-hills.html`
- **Darling Harbour (Chateau de Venus)**: `https://www.booking.com/hotel/au/chateau-de-venus.html`

---

## Tech Stack

- **Backend**: Python 3.11+ / FastAPI
- **Database**: SQLite (`data/azzurro_reviews.db`) with SHA-256 deduplication
- **Scraper**: `requests` + `BeautifulSoup4` with fallback sync
- **Frontend**: Plain HTML, vanilla JavaScript, Chart.js, precompiled Tailwind CSS (no Node build step needed)

---

## Local Setup

```bash
git clone https://github.com/saad07072/azzurro-review-insights.git
cd azzurro-review-insights
pip install -r requirements.txt
python main.py
```

Open `http://localhost:8000` in your browser. API docs are available at `http://localhost:8000/docs`.

---

## Architecture & Code Structure

```
├── app/
│   ├── config.py         # Property metadata and topic keyword lists
│   ├── database.py       # SQLite connection and query helpers
│   ├── scraper.py        # Booking.com scraper and fallback sync
│   ├── nlp_insights.py   # Topic classification and weekly metrics
│   ├── api.py            # FastAPI routes
│   └── seed_data.py      # Seed reviews for initial DB bootstrap
├── static/
│   ├── index.html        # Dashboard layout
│   ├── css/              # Local CSS (tailwind + custom styling)
│   └── js/               # Frontend logic and charts
├── data/
│   ├── azzurro_reviews.db
│   └── sample_reviews.json
├── main.py
├── requirements.txt
└── render.yaml
```

---

## Review Collection Method & Limitations

Booking.com does not provide a public API for reviews. Direct scraping (`app/scraper.py`) attempts to fetch and parse the hotel pages with desktop User-Agents.

### Challenge: Anti-Bot Interstitials
Booking.com uses Kasada/PerimeterX bot detection, which returns HTTP 202 challenge pages when accessed through standard HTTP requests.

### How this project handles it:
1. **Fallback sync**: When the scraper hits a 202 or rate limit, it falls back to updating the local database with verified baseline reviews and newly posted records so the dashboard remains functional.
2. **Deduplication**: Every review is hashed (`sha256(property_id + reviewer_name + date + text[:100])`). Duplicate records are ignored on insert via SQLite unique constraints.
3. **Production recommendation**: In a real production deployment, scraping Booking.com reliably requires residential proxy rotation (e.g. Bright Data) or a headless browser service (Playwright / Puppeteer) that can handle JavaScript challenges and cookie sessions.

---

## Insights Methodology

### Topic Classification
Reviews are scanned for keywords across 8 operational categories:
- Cleanliness
- Check-in experience
- Staff or receptionist behaviour
- Noise
- Facilities
- Location
- Room condition
- Value for money

To avoid false complaints (e.g. a review saying *"Great location, but shower was dirty"*), the percentage breakdown for operational issues is calculated specifically from negative review text rather than positive feedback.

---

## Deployment

The app is deployed on Render as a web service:
- **Build command**: `pip install -r requirements.txt`
- **Start command**: `python main.py`
- Environment variables: `PORT` is bound dynamically by `main.py`.
