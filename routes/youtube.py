"""
This module contains the handlers related to the youtube videos section.
"""

import requests
from xml.etree import ElementTree
from flask import jsonify

from app_prepare import app, cache


from flask import request


@app.route("/api/videos/latest")
def get_latest_videos():
    """
    Get the latest videos from the youtube channel with a given ID and parse the XML
    response to return a list of videos.
    """
    # Get number of videos from query parameter
    n_param = request.args.get("n", default=None, type=int)
    if n_param is None:
        n = 5
    else:
        n = n_param
    fetch_all = n == 0

    """
    Get the latest videos from the youtube channel with a given ID and parse the XML
    response to return a list of videos.
    """
    data = cache.get("recent_videos")

    if data and n == 5:
        return jsonify(data)

    # YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
    YOUTUBE_CHANNEL_ID = "UCUwcvD9rSzUW3JhpP2FMItQ"
    RSS_URL = (
        f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"
    )

    RSS_response = requests.get(RSS_URL)
    RSS_response.raise_for_status()

    root = ElementTree.fromstring(RSS_response.content)
    recent_videos = []
    counter = 0
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        # Filter out the shorts
        link = entry.find("{http://www.w3.org/2005/Atom}link").get("href")
        if "shorts" in link:
            continue

        recent_videos.append(
            {
                "title": entry.find("{http://www.w3.org/2005/Atom}title").text,
                "link": entry.find("{http://www.w3.org/2005/Atom}link").get("href"),
                "thumbnail": entry.find("{http://search.yahoo.com/mrss/}group")
                .find("{http://search.yahoo.com/mrss/}thumbnail")
                .get("url"),
                "description": entry.find("{http://search.yahoo.com/mrss/}group")
                .find("{http://search.yahoo.com/mrss/}description")
                .text,
                "published": entry.find("{http://www.w3.org/2005/Atom}published").text,
            }
        )
        counter += 1
        if not fetch_all and counter >= n:
            break

    cache.set("recent_videos", recent_videos, timeout=600)
    return jsonify(recent_videos)
