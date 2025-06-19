from typing import Optional
from dataclasses import dataclass

@dataclass
class YouTubeError:
    """Custom error class for YouTube API wrapper"""
    error_type: str
    message: str
    details: Optional[str] = None

@dataclass
class YouTubeVideoBuilder:
    """Custom video object builder for YouTube videos"""
    video_id: str
    title: str
    description: str
    author: str
    channel_id: str
    length_seconds: int
    view_count: int
    keywords: list
    upload_date: str
    category: str
    thumbnail_url: str
