from typing import Dict, List, Optional, Union
from .models import YouTubeError
import re
import json

def _extract_player_response(html_content: str) -> Optional[str]:
    """
    Extract ytInitialPlayerResponse JSON from HTML content
    """
    patterns = [
        r'ytInitialPlayerResponse\s*=\s*({.+?});',
        r'ytInitialPlayerResponse":\s*({.+?}),'
    ]
    for pattern in patterns:
        match = re.search(pattern, html_content, re.DOTALL)
        if match:
            return match.group(1)
    return None

def _extract_initial_data(html_content: str) -> Optional[str]:
    """
    Extract ytInitialPlayerResponse JSON from HTML content
    """
    patterns = [
        r'ytInitialData\s*=\s*({.+?});',
        r'ytInitialData":\s*({.+?}),'
    ]
    for pattern in patterns:
        match = re.search(pattern, html_content, re.DOTALL)
        if match:
            return match.group(1)
    return None



def _extract_search_results(html_content: str) -> List[Dict]:
    """
    Extract video results from YouTube search HTML.
    Each result includes: channel id, channel name, thumbnail url, view count, video duration, video id, title.
    """
    # Find initial data JSON
    initial_data_match = re.search(r'var ytInitialData = ({.*?});</script>', html_content, re.DOTALL)
    if not initial_data_match:
        initial_data_match = re.search(r'window\["ytInitialData"\]\s*=\s*({.+?});', html_content, re.DOTALL)
    if not initial_data_match:
        return []
    try:
        data = json.loads(initial_data_match.group(1))
    except Exception:
        return []
    results = []
    # Traverse to videoRenderer objects in search results
    try:
        contents = (
            data["contents"]["twoColumnSearchResultsRenderer"]
            ["primaryContents"]["sectionListRenderer"]["contents"]
        )
        for section in contents:
            items = section.get("itemSectionRenderer", {}).get("contents", [])
            for item in items:
                video = item.get("videoRenderer")
                if video:
                    # Extract required fields, some may be missing
                    video_id = video.get("videoId")
                    title = video.get("title", {}).get("runs", [{}])[0].get("text")
                    thumbnail_url = ""
                    thumbnails = video.get("thumbnail", {}).get("thumbnails", [])
                    if thumbnails:
                        thumbnail_url = thumbnails[-1].get("url", "")
                    view_count_text = video.get("viewCountText", {}).get("simpleText") or ""
                    duration = video.get("lengthText", {}).get("simpleText", "")
                    channel_name = ""
                    channel_id = ""
                    owner = video.get("ownerText", {}).get("runs", [{}])[0]
                    channel_name = owner.get("text", "")
                    channel_id = owner.get("navigationEndpoint", {}).get("browseEndpoint", {}).get("browseId", "")
                    results.append({
                        "video_id": video_id,
                        "title": title,
                        "thumbnail_url": thumbnail_url,
                        "view_count_text": view_count_text,
                        "duration": duration,
                        "channel_id": channel_id,
                        "channel_name": channel_name,
                    })
    except Exception:
        return []
    return results
