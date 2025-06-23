import requests

try:
    import orjson as json
except ImportError:
    import json
    orjson = None


import ast
import re
import time
import logging
from typing import Dict, List, Optional, Union

from .models import YouTubeError
from .utils import _validate_query, _validate_video_id, _build_video_info_dict
from .parser import _extract_player_response, _extract_search_results, _extract_initial_data
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    
    def auto_complete(self, query: str) -> Union[List[str], YouTubeError]:
        """
        Fetch autocomplete suggestions for a search query
        
        Args:
            query: Search query string
            
        Returns:
            List of suggestion strings or YouTubeError object
        """
        try:
            _validate_query(query)
            
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
    
    def get_video_info(self, video_id: str) -> Union[Dict,YouTubeError]:
        """
        Fetch metadata for a YouTube video
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary containing video metadata or YouTubeError object
        """
        try:
            _validate_video_id(video_id)
            
            video_url = "https://www.youtube.com/watch"
            params = {"v": video_id.strip()}
            
            logger.info(f"Fetching video info for ID: {video_id}")
            response = self._make_request(video_url, params)
            
            html_content = response.text
            
            # Extract JSON data from HTML
            json_data = _extract_player_response(html_content)
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
            result = _build_video_info_dict(video_details, microformat)
            logger.info(f"Successfully extracted info for video: {result.get('title', 'Unknown')}")
            return result
            
        except YouTubeError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_video_info: {e}")
            return YouTubeError(
                error_type="UNEXPECTED_ERROR",
                message="An unexpected error occurred",
                details=str(e)
            ) 
    def search_videos(self, query: str, max_results: int = 10) -> Union[List[Dict], YouTubeError]:
            """
            Search YouTube for videos by keyword.

            Args:
                query: The search keyword.
                max_results: Maximum number of videos to return.

            Returns:
                A list of dicts, each with channel id, channel name, thumbnail url, view count, video duration, video id, and title.
                Or a YouTubeError on failure.
            """
            try:
                _validate_query(query)
                api_url = "https://www.youtube.com/results"
                params = {"search_query": query.strip()}
                logger.info(f"Searching YouTube for videos: '{query}'")
                response = self._make_request(api_url, params)
                html_content = response.text
                videos = _extract_search_results(html_content)
                if not videos:
                    return YouTubeError(
                        error_type="NO_RESULTS",
                        message="No videos found for the search query."
                    )
                return videos[:max_results]
            except YouTubeError:
                raise
            except Exception as e:
                logger.error(f"Unexpected error in search_videos: {e}")
                return YouTubeError(
                    error_type="UNEXPECTED_ERROR",
                    message="An unexpected error occurred during search.",
                    details=str(e)
                )
    def get_channel_info(self,channel_id: str) -> Union[Dict,YouTubeError]:
        """
        """
        response = self._make_request(f"https://youtube.com/channel/{channel_id}")
        data = _extract_initial_data(response.text)
        if not data:
            return YouTubeError(
                error_type="PLAYER_RESPONSE_NOT_FOUND",
                message="ytInitialPlayerResponse not found",
                details=""
            )
        json_data = json.loads(data)
        pageHeader = json_data['header']['pageHeaderRenderer']
        banner = pageHeader['content']['pageHeaderViewModel'].get('banner')
        result = {}
        result["banner_image"] = banner['imageBannerViewModel']['image']['sources'][-1]['url'] if banner else ""
        result["profile_image"] = json_data['microformat']['microformatDataRenderer']['thumbnail']['thumbnails'][0]['url']
        result["description"] = pageHeader['content']['pageHeaderViewModel']['description']['descriptionPreviewViewModel']['description']['content']
        result["channel_name"] = pageHeader['pageTitle']
        return result

    def __del__(self):
        """Close the session when the object is destroyed"""
        if hasattr(self, 'session'):
            self.session.close()
