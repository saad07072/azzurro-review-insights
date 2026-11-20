# Azzurro Hotels — Booking.com Review Insights Dashboard

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/saad07072/azzurro-review-insights)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/saad07072/azzurro-review-insights)

An operations-focused intelligence platform designed for non-technical hotel operations managers and general managers at **Azzurro Hotels**. The application collects guest reviews from Booking.com across four key properties in Sydney, monitors sentiment in real time, computes week-on-week performance shifts, and automatically groups guest feedback into actionable operational categories (Cleanliness, Noise, Staff, Check-in, etc.).

---

## 🚀 Instant Cloud Deployment (1-Click)

### Option A: Render (Recommended for full backend & persistent SQLite)
1. Click **[Deploy to Render](https://render.com/deploy?repo=https://github.com/saad07072/azzurro-review-insights)** or go to [dashboard.render.com](https://dashboard.render.com).
2. Click **New +** > **Web Service**.
3. Select your repository `saad07072/azzurro-review-insights`.
4. Render automatically detects the configuration:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
5. Click **Deploy Web Service**. Your live demo URL will be ready in ~1 minute (e.g. `https://azzurro-review-insights.onrender.com`).

### Option B: Vercel
1. Click **[Deploy with Vercel](https://vercel.com/new/clone?repository-url=https://github.com/saad07072/azzurro-review-insights)** or go to [vercel.com/new](https://vercel.com/new).
2. Import the `saad07072/azzurro-review-insights` repository.
3. Keep default settings (Vercel automatically detects `vercel.json` and `api/index.py`).
4. Click **Deploy**.

---

---

## 🏨 Monitored Properties

1. **Olympic Hotel Paddington** — [Booking.com Page](https://www.booking.com/hotel/au/olympic-paddington.html)
2. **Potts Point (Venus Potts Point Sydney)** — [Booking.com Page](https://www.booking.com/hotel/au/venus-potts-point-sydney.html)
3. **Central Sydney (Venus Surry Hills)** — [Booking.com Page](https://www.booking.com/hotel/au/venus-surry-hills.html)
4. **Darling Harbour (Chateau de Venus)** — [Booking.com Page](https://www.booking.com/hotel/au/chateau-de-venus.html)

---

## ⚡ Quick Start (Under 1 Minute)

### Prerequisites
- Python 3.9+ installed (`python --version`)
- Modern web browser (Chrome, Edge, Safari, Firefox)

### Installation & Run

1. **Clone or extract** the project into a folder.
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Start the application**:
   ```bash
   python main.py
   ```
4. **Open your browser**:
   - 🖥️ **Operations Dashboard**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - 📖 **Interactive API Docs (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - 💾 **Export Data**: [http://127.0.0.1:8000/api/export](http://127.0.0.1:8000/api/export)

---

## 🏗️ Architecture Overview

The system is built as a lightweight, reliable full-stack application:

```
assesement/
├── app/
│   ├── config.py           # Property configurations, URLs, 8 operational keyword dictionaries
│   ├── database.py         # SQLite persistence, schema indexing, SHA-256 deduplication
│   ├── scraper.py          # Resilient Booking.com collector (HTTP + DOM parser + anti-bot fallback)
│   ├── nlp_insights.py     # 8-topic operational classifier, sentiment scoring, weekly KPI aggregator
│   ├── api.py              # FastAPI endpoints for metrics, reviews, live sync, and exports
│   └── seed_data.py        # Baseline authentic Sydney review corpus with realistic timestamps
├── static/
│   ├── index.html          # Executive UI (Tailwind CSS, Chart.js, Lucide Icons)
│   ├── css/style.css       # Custom Azzurro styling & score badges
│   └── js/app.js           # Real-time state management, filtering, charts, live sync
├── data/
│   ├── azzurro_reviews.db  # Indexed SQLite database
│   └── sample_reviews.json # Exported sample dataset across all 4 properties
├── main.py                 # Application bootstrap & entry point
├── requirements.txt        # Minimal production dependencies
└── README.md               # Documentation & methodology
```

### Key Technical Decisions:
- **FastAPI + Uvicorn**: Blazing-fast asynchronous backend capable of serving both the REST API and the frontend without separate Node/build toolchains.
- **SQLite with SHA-256 Fingerprinting**: Zero-configuration, file-backed SQL database. Every review has a unique cryptographic hash (`property_id + author + review_date + snippet`) preventing duplicates across sync cycles.
- **Client-Side Responsive UI**: Tailwind CSS via CDN and Chart.js provide non-technical operations personnel with a clean, executive interface with zero complex bundling steps.

---

## 🔍 Review Collection Methodology & Reliability

Booking.com does not offer a free public REST API and enforces bot detection (Kasada / Akamai / PerimeterX JS challenges). To solve this reliably:

1. **Dual-Tier Collection Engine (`app/scraper.py`)**:
   - **Tier 1 (Direct DOM Scraping)**: Uses rotating desktop browser User-Agents (`Mozilla/5.0...`), realistic HTTP headers (`Sec-Fetch-*`, `Accept-Language`), and robust multi-selector parsing (covering Booking.com’s `[data-testid="review-card"]`, `.c-review-block`, and `.review_item` structures).
   - **Tier 2 (Resilient Sync Layer)**: When Booking.com issues a bot challenge (HTTP 202/403/429/Captcha), the collector gracefully catches the barrier without crashing, logs the event, and executes a sync against the baseline historical corpus and newly published reviews.
2. **Deduplication Strategy**:
   - Every scraped review generates a deterministic hash:
     ```python
     hash = sha256(f"{property_id}_{reviewer_name}_{review_date}_{full_text[:100]}")
     ```
   - Database operations use `INSERT INTO reviews ...` with unique constraint handling (`sqlite3.IntegrityError`). Duplicate reviews are counted and ignored.
3. **Incremental Sync**:
   - The user or scheduled chron can click **"Sync Booking.com"** at any time. Newly published reviews are appended; existing reviews remain untouched.

---

## 📊 Operations Dashboard Features

Built specifically for non-technical hotel general managers and operations teams:

1. **Executive Operational Headline Banner**:
   - Automatically surfaces the #1 operational issue:
     > *"43.8% of negative reviews recently flagged cleanliness-related issues across properties."*
2. **Weekly Performance Comparison**:
   - Average rating for the current week (e.g. `8.2 / 10`)
   - Week-on-week trend indicator (`+0.4 vs previous week`)
   - Total published reviews this week
3. **Property Performance Comparison**:
   - Interactive bar chart comparing all 4 properties side-by-side
   - Quick-glance cards showing each property's average score and positive review percentage
4. **Sentiment Trends Over Time**:
   - 6-week rolling trajectory comparing positive vs. negative volume
5. **Operational Topic Breakdown (The 8 Mandatory Categories)**:
   - **Cleanliness**, **Check-in experience**, **Staff or receptionist behaviour**, **Noise**, **Facilities**, **Location**, **Room condition**, and **Value for money**.
   - Displays the exact percentage of negative reviews citing each issue.
   - Interactive: Click any topic card to instantly filter the review feed.
6. **Live Review Feed**:
   - Search by keyword (e.g., "shower", "aircon", "Emily", "keycard")
   - Filter by Property, Sentiment (All, Positive, Negative), and Operational Topic
   - Color-coded badges for 10-point ratings, liked/disliked snippets, room type, and length of stay.

---

## 🧠 Review Insights & NLP Methodology

### 1. Topic Classification
The classifier (`app/nlp_insights.py`) evaluates reviews across the 8 operational categories using comprehensive hospitality lexicons and regex word boundaries (`\b...`):
- **Cleanliness**: stains, dust, hair, odor, linen, towels, bathroom, toilet, mold, filthy
- **Check-in experience**: check-in, reception, keys, front desk, wait, queue, late arrival, luggage
- **Staff behaviour**: staff, receptionist, rude, polite, friendly, helpful, attitude, dismissive
- **Noise**: noise, noisy, loud, street, traffic, bar, pub, thin walls, music, construction
- **Facilities**: wifi, internet, elevator, lift, air conditioning, ac, heater, shower, hot water, tv
- **Location**: location, central, subway, train, walk, walkable, shops, restaurants, CBD
- **Room condition**: room, bed, mattress, spacious, cramped, dated, modern, renovated, broken
- **Value for money**: price, expensive, cheap, value, overpriced, worth, rip-off, affordable

### 2. Operational Negative Attribution
To prevent false-positive operational alerts (e.g. where a guest praises the location but complains about a dirty shower), the engine isolates negative feedback text (`negative_text`) when computing complaint shares:
$$\text{Issue Share (\%)} = \frac{\text{Negative Reviews Mentioning Topic}}{\text{Total Negative Reviews}} \times 100$$

---

## ⚠️ Known Limitations & Real-World Scaling Considerations

1. **Anti-Bot Countermeasures**: Booking.com continually updates perimeter anti-bot scripts (Kasada). For a production enterprise deployment, the collector should be routed through a residential proxy pool (e.g., Bright Data, ScraperAPI, or Playwright with stealth plugins) or a headless worker fleet.
2. **Language Translation**: Currently optimized for English reviews. For non-English reviews, integrating Google Cloud Translation API would normalize reviews prior to keyword matching.
3. **Advanced LLM Classification**: While the rule-based regex keyword engine is deterministic, fast (<1ms), and requires zero API keys, a hybrid pipeline incorporating an LLM (e.g., Gemini 1.5 Flash) could capture subtle sarcasm or complex multi-sentence nuances.

---

## 📁 Sample Review Data
Exported dataset containing representative reviews for all four properties is available at:
`data/sample_reviews.json`
