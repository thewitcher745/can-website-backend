from flask_cors import CORS
from flask import Flask
from flask_caching import Cache

app = Flask(__name__)

CORS(app)  # This enables CORS for all routes

# Enabling caching on the app
cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 3600})
cache.init_app(app)
