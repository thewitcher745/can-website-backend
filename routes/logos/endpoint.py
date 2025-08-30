"""
This endpoint solely exists to return the link to the logo of a coin
as a response.
Takes the coin name as slug.
"""

from flask import jsonify

from app_prepare import app
from .get_logo_link import get_logo_link_from_symbol


@app.route("/api/logo/<slug>")
def get_logo_link(slug: str):
    return jsonify(get_logo_link_from_symbol(slug))
