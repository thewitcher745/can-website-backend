from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_caching import Cache
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configure CORS with specific allowed origins
ALLOWED_ORIGINS = [
    "https://can-trading.com",  # Replace with your actual Netlify domain
    "https://can-website-staging.netlify.app",  # Staging
    "http://localhost:3000",  # For local development
]

# Enable CORS with specific origins
cors = CORS(
    app,
    resources={
        r"/*": {
            "origins": ALLOWED_ORIGINS,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    },
)


# Add before_request handler to validate Origin header
@app.before_request
def check_origin():
    if request.method == "OPTIONS":
        return None  # Let the CORS headers handle OPTIONS requests

    origin = request.headers.get("Origin")
    if origin and origin not in ALLOWED_ORIGINS:
        return jsonify({"error": "Access denied"}), 403
    return None


# Enabling caching on the app
cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 3600})
cache.init_app(app)
