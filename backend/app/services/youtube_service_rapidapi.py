"""YouTube transcript fetching service using RapidAPI"""
import requests
import re
import os
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class YouTubeServiceRapidAPI:
    """Service for fetching YouTube video transcripts via RapidAPI"""

    # RapidAPI configuration
    RAPIDAPI_HOST = "youtube-transcript3.p.rapidapi.com"
    RAPIDAPI_ENDPOINT = "https://youtube-transcript3.p.rapidapi.com/api/transcript"

    @staticmethod
    def get_thumbnail_url(video_id: str, quality: str = "maxresdefault") -> str:
        """
        Get thumbnail URL for a YouTube video

        Args:
            video_id: YouTube video ID
            quality: Thumbnail quality (maxresdefault, sddefault, hqdefault, mqdefault, default)

        Returns:
            URL string for the thumbnail
        """
        return f"https://img.youtube.com/vi/{video_id}/{quality}.jpg"

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats
        """
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        # If it's already just an ID (11 characters)
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url

        return None

    @staticmethod
    def get_transcript(video_url: str, languages: List[str] = None) -> Dict[str, any]:
        """
        Fetch transcript for a YouTube video using RapidAPI

        Args:
            video_url: YouTube video URL or video ID
            languages: List of language codes to try (default: ['en'])

        Returns:
            Dictionary with transcript data and metadata
        """
        if languages is None:
            languages = ['en']

        # Extract video ID from URL
        video_id = YouTubeServiceRapidAPI.extract_video_id(video_url)
        if not video_id:
            return {
                "success": False,
                "error": "Invalid YouTube URL or video ID",
                "transcript": None,
                "video_id": None
            }

        # Get RapidAPI key from environment
        rapidapi_key = os.getenv('RAPIDAPI_KEY')
        if not rapidapi_key:
            logger.error("❌ RAPIDAPI_KEY not configured")
            return {
                "success": False,
                "error": "RapidAPI key not configured on server",
                "transcript": None,
                "video_id": video_id
            }

        try:
            # Prepare request
            headers = {
                "x-rapidapi-key": rapidapi_key,
                "x-rapidapi-host": YouTubeServiceRapidAPI.RAPIDAPI_HOST
            }

            params = {
                "videoId": video_id,
                "lang": languages[0] if languages else "en"
            }

            logger.info(f"🎬 Fetching transcript via RapidAPI for video: {video_id}")

            # Make request to RapidAPI
            response = requests.get(
                YouTubeServiceRapidAPI.RAPIDAPI_ENDPOINT,
                headers=headers,
                params=params,
                timeout=30
            )

            # Check response
            if response.status_code != 200:
                logger.error(f"❌ RapidAPI error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"RapidAPI returned status {response.status_code}",
                    "transcript": None,
                    "video_id": video_id
                }

            data = response.json()

            # Log the response for debugging
            logger.info(f"📦 RapidAPI response type: {type(data)}, data: {data}")

            # Check if transcript was found
            if not isinstance(data, dict):
                logger.error(f"❌ Response is not a dict: {type(data)} = {data}")
                return {
                    "success": False,
                    "error": f"Invalid response from RapidAPI: {str(data)[:100]}",
                    "transcript": None,
                    "video_id": video_id
                }

            if 'transcript' not in data:
                logger.error(f"❌ No transcript field in response: {data}")
                return {
                    "success": False,
                    "error": f"No transcript found for video in language: {languages[0]}",
                    "transcript": None,
                    "video_id": video_id
                }

            # Parse transcript from RapidAPI response
            transcript_items = data.get('transcript', [])
            if not transcript_items:
                return {
                    "success": False,
                    "error": "Transcript is empty",
                    "transcript": None,
                    "video_id": video_id
                }

            logger.info(f"✅ Transcript fetched successfully! Length: {len(transcript_items)}")

            # Format transcript as continuous text
            # Note: RapidAPI uses HTML entities, need to decode
            import html
            full_text = " ".join([html.unescape(str(item.get('text', ''))) for item in transcript_items])

            # Also provide timestamped version
            # RapidAPI uses 'offset' instead of 'start'
            timestamped = [
                {
                    "text": html.unescape(str(item.get('text', ''))),
                    "start": float(item.get('offset', 0)),
                    "duration": float(item.get('duration', 0))
                }
                for item in transcript_items
            ]

            # Generate thumbnail URLs
            thumbnail_url = YouTubeServiceRapidAPI.get_thumbnail_url(video_id, "maxresdefault")
            thumbnail_url_hq = YouTubeServiceRapidAPI.get_thumbnail_url(video_id, "hqdefault")

            return {
                "success": True,
                "error": None,
                "video_id": video_id,
                "transcript": full_text,
                "timestamped_transcript": timestamped,
                "language": languages[0],
                "word_count": len(full_text.split()),
                "thumbnail_url": thumbnail_url,
                "thumbnail_url_hq": thumbnail_url_hq
            }

        except requests.RequestException as e:
            logger.error(f"❌ Network error: {str(e)}")
            return {
                "success": False,
                "error": f"Network error: {str(e)[:200]}",
                "transcript": None,
                "video_id": video_id
            }
        except Exception as e:
            import traceback
            logger.error(f"❌ Unexpected error: {str(e)}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            return {
                "success": False,
                "error": f"Error fetching transcript: {str(e)[:200]}",
                "transcript": None,
                "video_id": video_id
            }

    @staticmethod
    def list_available_transcripts(video_url: str) -> Dict[str, any]:
        """
        List all available transcripts for a video

        Note: RapidAPI's YouTube Transcript3 API might not support listing
        available languages. This method returns a basic response.

        Args:
            video_url: YouTube video URL or video ID

        Returns:
            Dictionary with available transcript languages
        """
        video_id = YouTubeServiceRapidAPI.extract_video_id(video_url)
        if not video_id:
            return {
                "success": False,
                "error": "Invalid YouTube URL or video ID",
                "transcripts": []
            }

        # RapidAPI endpoint doesn't expose language listing
        # Return common languages that might be available
        return {
            "success": True,
            "error": None,
            "video_id": video_id,
            "transcripts": [
                {"language": "English", "language_code": "en", "is_generated": True, "is_translatable": False}
            ]
        }


# Create singleton instance
youtube_service_rapidapi = YouTubeServiceRapidAPI()
