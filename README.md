# Flask Blog API

This project is a Flask-based backend that serves Markdown blog posts with YAML front matter as an API. Blog posts are stored as `.md` files in the `blog_posts/` directory.

## Endpoints
- `/api/blog/` — List all blog posts (metadata only)
- `/api/blog/<slug>` — Get a single blog post (metadata + rendered HTML)

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run the server: `python app.py`

Blog posts can be added by placing new `.md` files into the `blog_posts/` directory.
