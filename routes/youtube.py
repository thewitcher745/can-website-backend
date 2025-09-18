"""
This module contains the handlers related to the youtube videos section.
"""

import os
import requests
from xml.etree import ElementTree
from flask import jsonify

from app_prepare import app, cache


@app.route("/api/videos/latest")
def get_latest_videos(n: int = 5):
    """
    Get the latest videos from the youtube channel with a given ID and parse the XML
    response to return a list of videos.
    """
    data = cache.get("recent_videos")

    if data:
        return jsonify(data)

    # YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
    YOUTUBE_CHANNEL_ID = "UCUwcvD9rSzUW3JhpP2FMItQ"
    RSS_URL = (
        f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"
    )

    RSS_response = requests.get(RSS_URL)
    RSS_response.raise_for_status()

    RSS_content = RSS_response.content

    # Use an XML parsing library to get the n most recent videos
    root = ElementTree.fromstring(RSS_content)

    recent_videos = []
    counter = 0
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        # Filter out the shorts
        link = entry.find("{http://www.w3.org/2005/Atom}link").get("href")
        if "shorts" in link:
            continue

        counter += 1
        recent_videos.append(
            {
                "id": entry.find(
                    "{http://www.youtube.com/xml/schemas/2015}videoId"
                ).text,
                "title": entry.find("{http://www.w3.org/2005/Atom}title").text,
                "link": entry.find("{http://www.w3.org/2005/Atom}link").get("href"),
                "thumbnail": entry.find("{http://search.yahoo.com/mrss/}group")
                .find("{http://search.yahoo.com/mrss/}thumbnail")
                .get("url"),
                "published": entry.find("{http://www.w3.org/2005/Atom}published").text,
            }
        )

        if counter == n:
            break

    cache.set("recent_videos", recent_videos, timeout=600)
    return jsonify(recent_videos)
