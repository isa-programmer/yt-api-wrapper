import requests
import json
import ast
import re
import time
import logging
from typing import Dict, List, Optional, Union
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class YouTubeAPIWrapper:
    """
    Enhanced YouTube API wrapper with improved error handling and reliability
    """
    
    def __init__(self, timeout: int = 10, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize YouTube API wrapper
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> requests.Response:
        """
        Make HTTP request with retry logic
        
        Args:
            url: Request URL
            params: Query parameters
            
        Returns:
            Response object
            
        Raises:
            YouTubeError: If request fails after all retries
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=self.timeout
                )
                
                if response.ok:
                    return response
                else:
                    logger.warning(f"HTTP {response.status_code} on attempt {attempt + 1}")
                    if attempt < self.max_retries:
                        time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                        continue
                    else:
                        raise YouTubeError(
                            error_type="HTTP_ERROR",
                            message=f"HTTP {response.status_code}",
                            details=response.text[:200]
                        )
                        
            except requests.exceptions.RequestException as e:
                last_exception = e
                logger.warning(f"Request failed on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
        
        raise YouTubeError(
            error_type="REQUEST_FAILED",
            message="Request failed after all retries",
            details=str(last_exception)
        )
    
    def _validate_query(self, query: str) -> None:
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
    
    def _validate_video_id(self, video_id: str) -> None:
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
    
    def auto_complete(self, query: str) -> Union[List[str], YouTubeError]:
        """
        Fetch autocomplete suggestions for a search query
        
        Args:
            query: Search query string
            
        Returns:
            List of suggestion strings or YouTubeError object
        """
        try:
            self._validate_query(query)
            
            api_url = "https://suggestqueries-clients6.youtube.com/complete/search"
            params = {
                "q": query.strip(),
                "client": "youtube",
                "hl": "en",  # Language
                "gl": "US"   # Geographic location
            }
            
            logger.info(f"Fetching autocomplete for query: '{query}'")
            response = self._make_request(api_url, params)
            
            # Parse the JSONP response
            response_text = response.text
            if not response_text.startswith('window.google.ac.h('):
                raise YouTubeError(
                    error_type="PARSE_ERROR",
                    message="Unexpected response format",
                    details=response_text[:100]
                )
            
            # Extract JSON from JSONP
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                raise YouTubeError(
                    error_type="PARSE_ERROR",
                    message="Could not find JSON data in response"
                )
            
            json_str = response_text[json_start:json_end]
            
            try:
                data = ast.literal_eval(json_str)
            except (SyntaxError, ValueError) as e:
                raise YouTubeError(
                    error_type="PARSE_ERROR",
                    message="Failed to parse JSON response",
                    details=str(e)
                )
            
            # Extract suggestions
            if len(data) < 2 or not isinstance(data[1], list):
                return []
            
            suggestions = []
            for item in data[1]:
                if isinstance(item, list) and len(item) > 0:
                    suggestions.append(item[0])
            
            logger.info(f"Found {len(suggestions)} suggestions")
            return suggestions
            
        except YouTubeError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in auto_complete: {e}")
            return YouTubeError(
                error_type="UNEXPECTED_ERROR",
                message="An unexpected error occurred",
                details=str(e)
            )
    
    def get_video_info(self, video_id: str) -> Union[YouTubeVideoBuilder, YouTubeError]:
        """
        Fetch metadata for a YouTube video
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary containing video metadata or YouTubeError object
        """
        try:
            self._validate_video_id(video_id)
            
            video_url = "https://www.youtube.com/watch"
            params = {"v": video_id.strip()}
            
            logger.info(f"Fetching video info for ID: {video_id}")
            response = self._make_request(video_url, params)
            
            html_content = response.text
            
            # Extract JSON data from HTML
            json_data = self._extract_player_response(html_content)
            if not json_data:
                return YouTubeError(
                    error_type="PARSE_ERROR",
                    message="Could not find player response data"
                )
            
            try:
                data = json.loads(json_data)
            except json.JSONDecodeError as e:
                return YouTubeError(
                    error_type="PARSE_ERROR",
                    message="Failed to parse video data JSON",
                    details=str(e)
                )
            
            # Extract video details
            video_details = data.get("videoDetails")
            if not video_details:
                return YouTubeError(
                    error_type="VIDEO_NOT_FOUND",
                    message="Video details not found (video may be private, deleted, or restricted)"
                )
            
            # Extract microformat data
            microformat = data.get("microformat", {}).get("playerMicroformatRenderer", {})
            
            # Build result dictionary
            result = self._build_video_info_dict(video_details, microformat)
            logger.info(f"Successfully extracted info for video: {result.get('title', 'Unknown')}")
            return YouTubeVideoBuilder(**result)
            
        except YouTubeError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_video_info: {e}")
            return YouTubeError(
                error_type="UNEXPECTED_ERROR",
                message="An unexpected error occurred",
                details=str(e)
            )
    
    def _extract_player_response(self, html_content: str) -> Optional[str]:
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
    
    def _build_video_info_dict(self, video_details: Dict, microformat: Dict) -> Dict:
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
    
    def __del__(self):
        """Close the session when the object is destroyed"""
        if hasattr(self, 'session'):
            self.session.close()
