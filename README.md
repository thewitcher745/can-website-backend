# CAN Website Backend

A Flask-based backend powering the CAN platform. It serves Markdown-based blog and analysis posts as a RESTful API, and provides technicals data (top crypto gainers) via web scraping.

## Features
- Serve blog posts (Markdown with YAML front matter) via API
- Serve analysis/roadmap posts (Markdown with multi-section YAML) via API
- Scrape and serve top crypto gainers from CoinMarketCap
- Caching for performance
- CORS enabled for all endpoints

## Project Structure
```
CAN-website-backend/
├── app.py                # Main entry point
├── app_prepare.py        # Flask app and cache setup
├── requirements.txt      # Python dependencies
├── routes/               # API endpoints (blog, analysis, technicals)
│   ├── blog_posts.py
│   ├── analysis_posts.py
│   ├── general.py
│   └── technicals/
│       └── top_gainers/
│           ├── endpoint.py
│           ├── data_fetching.py
│           └── urls.py
├── blog_posts/           # Markdown blog posts
├── analysis_posts/       # Markdown analysis posts
├── utils/                # Utility functions
└── README.md
```

## API Endpoints
### General
- `GET /` — API root, health/info message

### Blog Posts
- `GET /api/blog/` — List all blog posts (metadata only)
- `GET /api/blog/<slug>` — Get a single blog post (metadata + rendered HTML)

### Analysis Posts
- `GET /api/analysis/` — List all analysis posts (metadata only)
- `GET /api/analysis/<slug>` — Get a single analysis post (main + updates, metadata + rendered HTML)

### Technicals: Top Gainers
- `GET /api/top_gainers` — Get the latest list of top crypto gainers (scraped from CoinMarketCap)

## Setup & Usage
1. **Clone the repo:**
   ```sh
   git clone https://github.com/thewitcher745/can-website-backend.git
   cd can-website-backend
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Run the server:**
   ```sh
   python app.py
   ```
   The server will run on `http://localhost:5000` by default.

4. **Add Content:**
   - Blog posts: place `.md` files in `blog_posts/`
   - Analysis posts: place `.md` files in `analysis_posts/`

## Dependencies
- Flask
- Flask-Caching
- flask-cors
- Markdown
- PyYAML
- requests
- beautifulsoup4

(See `requirements.txt` for full list)

## Description
This backend is designed for content-driven platforms, especially in crypto/finance. It enables easy publishing of Markdown-based content, exposes robust API endpoints for frontend consumption, and incorporates real-time technical data via web scraping. Caching and CORS are enabled for smooth client integration.

---
**Last updated:** 2025-08-11
