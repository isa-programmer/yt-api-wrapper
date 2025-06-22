from typing import Dict, List, Optional, Union
from .models import YouTubeError
import re


def _validate_query(query: str) -> None:
    """
    Validate search query
    
    Args:
        query: Search query string
        
    Raises:
        YouTubeError: If query is invalid
    """
    if not query or not query.strip():
        raise YouTubeError(
            error_type="INVALID_INPUT",
            message="Query cannot be empty"
        )
    
    if len(query) > 200:
        raise YouTubeError(
            error_type="INVALID_INPUT",
            message="Query too long (max 200 characters)"
        )



def _validate_video_id(video_id: str) -> None:
    """
    Validate YouTube video ID format
    
    Args:
        video_id: YouTube video ID
        
    Raises:
        YouTubeError: If video ID is invalid
    """
    if not video_id or not video_id.strip():
        raise YouTubeError(
            error_type="INVALID_INPUT",
            message="Video ID cannot be empty"
        )
    
    # YouTube video IDs are 11 characters long and contain alphanumeric characters, hyphens, and underscores
    if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id.strip()):
        raise YouTubeError(
            error_type="INVALID_INPUT",
            message="Invalid YouTube video ID format"
        )


def _build_video_info_dict(video_details: Dict, microformat: Dict) -> Dict:
    """
    Build a clean video information dictionary
    
    Args:
        video_details: Video details from YouTube API
        microformat: Microformat data from YouTube API
        
    Returns:
        Dictionary with video information
    """
    result = {}
    
    # Video details fields
    video_fields = {
        "video_id": "videoId",
        "title": "title",
        "description": "shortDescription",
        "author": "author",
        "channel_id": "channelId",
        "length_seconds": "lengthSeconds",
        "view_count": "viewCount",
        "keywords": "keywords",
        "thumbnail": "thumbnail"
    }
    
    # Microformat fields
    microformat_fields = {
        "upload_date": "uploadDate",
        "category": "category"
    }
    
    # Extract video details
    for result_key, api_key in video_fields.items():
        value = video_details.get(api_key)
        if value is not None:
            # Convert numeric strings to integers where appropriate
            if result_key in ["length_seconds", "view_count"] and isinstance(value, str):
                try:
                    value = int(value)
                except ValueError:
                    pass
            result[result_key] = value
    
    # Extract microformat data
    for result_key, api_key in microformat_fields.items():
        value = microformat.get(api_key)
        if value is not None:
            result[result_key] = value
    
    # Extract thumbnail URL if available
    if "thumbnail" in result and isinstance(result["thumbnail"], dict):
        thumbnails = result["thumbnail"].get("thumbnails", [])
        if thumbnails:
            # Get the highest quality thumbnail
            result["thumbnail_url"] = thumbnails[-1].get("url", "")
        del result["thumbnail"]
    return result
