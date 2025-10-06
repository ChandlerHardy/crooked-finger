"""YouTube transcript fetching service"""
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.proxies import GenericProxyConfig
import re
import time
import os
import logging
import requests
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

# Monkey-patch requests to add browser-like headers
original_request = requests.Session.request

def patched_request(self, method, url, **kwargs):
    """Add browser-like headers to all requests"""
    if 'headers' not in kwargs:
        kwargs['headers'] = {}

    # Add browser headers to mimic Chrome on macOS
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

    # Only add headers that aren't already set
    for key, value in default_headers.items():
        if key not in kwargs['headers']:
            kwargs['headers'][key] = value

    return original_request(self, method, url, **kwargs)

# Apply the monkey patch
requests.Session.request = patched_request


class YouTubeService:
    """Service for fetching YouTube video transcripts"""

    # Rate limiting: Track last request time
    _last_request_time = 0
    _min_request_interval = 2  # Minimum seconds between requests

    @staticmethod
    def get_thumbnail_url(video_id: str, quality: str = "maxresdefault") -> str:
        """
        Get thumbnail URL for a YouTube video

        Args:
            video_id: YouTube video ID
            quality: Thumbnail quality (maxresdefault, sddefault, hqdefault, mqdefault, default)
                    - maxresdefault: 1280x720 (if available)
                    - sddefault: 640x480
                    - hqdefault: 480x360
                    - mqdefault: 320x180
                    - default: 120x90

        Returns:
            URL string for the thumbnail
        """
        return f"https://img.youtube.com/vi/{video_id}/{quality}.jpg"

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats
        Supports:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
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
        Fetch transcript for a YouTube video

        Args:
            video_url: YouTube video URL or video ID
            languages: List of language codes to try (default: ['en'])

        Returns:
            Dictionary with transcript data and metadata
        """
        if languages is None:
            languages = ['en']

        # Extract video ID from URL
        video_id = YouTubeService.extract_video_id(video_url)
        if not video_id:
            return {
                "success": False,
                "error": "Invalid YouTube URL or video ID",
                "transcript": None,
                "video_id": None
            }

        try:
            # Rate limiting: Add delay between requests to avoid YouTube blocks
            current_time = time.time()
            time_since_last_request = current_time - YouTubeService._last_request_time
            if time_since_last_request < YouTubeService._min_request_interval:
                time.sleep(YouTubeService._min_request_interval - time_since_last_request)

            # Fetch transcript using new API (v1.2.2+)
            # Use proxy if configured via environment variables to avoid IP blocking
            proxy_config = None
            proxy_url = os.getenv('YOUTUBE_PROXY_URL')

            if proxy_url:
                logger.info(f"🔒 Using proxy: {proxy_url}")
                proxy_config = GenericProxyConfig(
                    http_url=proxy_url,
                    https_url=proxy_url
                )
            else:
                logger.info(f"⚠️ No proxy configured - using direct connection")

            api = YouTubeTranscriptApi(proxy_config=proxy_config)
            logger.info(f"🎬 Fetching transcript for video: {video_id}")
            transcript_result = api.fetch(video_id, languages=languages)
            logger.info(f"✅ Transcript fetched successfully! Length: {len(transcript_result)}")

            # Update last request time
            YouTubeService._last_request_time = time.time()

            # Format transcript as continuous text
            # Note: In v1.2.2+, transcript items are FetchedTranscriptSnippet objects
            full_text = " ".join([snippet.text for snippet in transcript_result])

            # Also provide timestamped version
            timestamped = [
                {
                    "text": snippet.text,
                    "start": snippet.start,
                    "duration": snippet.duration
                }
                for snippet in transcript_result
            ]

            # Generate thumbnail URLs
            thumbnail_url = YouTubeService.get_thumbnail_url(video_id, "maxresdefault")
            thumbnail_url_hq = YouTubeService.get_thumbnail_url(video_id, "hqdefault")

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

        except TranscriptsDisabled:
            return {
                "success": False,
                "error": "Transcripts are disabled for this video",
                "transcript": None,
                "video_id": video_id
            }
        except NoTranscriptFound:
            return {
                "success": False,
                "error": f"No transcript found in languages: {', '.join(languages)}",
                "transcript": None,
                "video_id": video_id
            }
        except Exception as e:
            error_msg = str(e)
            # Detect IP blocking errors
            if "blocking requests" in error_msg or "IPBlocked" in error_msg:
                return {
                    "success": False,
                    "error": "YouTube is temporarily blocking requests. This usually resolves itself in 15-30 minutes. Try using a different network or waiting before retrying.",
                    "transcript": None,
                    "video_id": video_id
                }
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

        Args:
            video_url: YouTube video URL or video ID

        Returns:
            Dictionary with available transcript languages
        """
        video_id = YouTubeService.extract_video_id(video_url)
        if not video_id:
            return {
                "success": False,
                "error": "Invalid YouTube URL or video ID",
                "transcripts": []
            }

        try:
            # List transcripts using new API (v1.2.2+)
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)

            available = []
            for transcript in transcript_list:
                available.append({
                    "language": transcript.language,
                    "language_code": transcript.language_code,
                    "is_generated": transcript.is_generated,
                    "is_translatable": transcript.is_translatable
                })

            return {
                "success": True,
                "error": None,
                "video_id": video_id,
                "transcripts": available
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error listing transcripts: {str(e)}",
                "transcripts": []
            }


# Create singleton instance
youtube_service = YouTubeService()
