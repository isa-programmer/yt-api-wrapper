from typing import Dict, List, Optional, Union
from .models import YouTubeError
import re

def _extract_player_response(html_content: str) -> Optional[str]:
    """
    Extract ytInitialPlayerResponse JSON from HTML content
    
    Args:
        html_content: HTML content from YouTube page
        
    Returns:
        JSON string or None if not found
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