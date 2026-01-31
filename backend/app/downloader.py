#!/usr/bin/python3
"""Refactored YouTube downloader module for web service."""

from __future__ import unicode_literals
import yt_dlp
import os
import logging
from pathlib import Path
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)


class DownloadLogger:
    """Custom logger for yt-dlp to capture download progress."""
    
    def __init__(self):
        self.last_file = None
        logger.debug("DownloadLogger initialized")
        
    def debug(self, msg):
        extract_message = "[ExtractAudio] Destination: "
        download_message = "[download] Destination: "
        merge_message = "[Merger] Merging formats into "
        if msg.startswith(extract_message):
            self.last_file = msg[len(extract_message):]
            logger.debug(f"yt-dlp debug: {msg}")
        elif msg.startswith(download_message):
            self.last_file = msg[len(download_message):]
            logger.debug(f"yt-dlp debug: {msg}")
        elif msg.startswith(merge_message):
            self.last_file = msg[len(merge_message):]
            logger.debug(f"yt-dlp debug: {msg}")
        else:
            logger.debug(f"yt-dlp: {msg}")

    def warning(self, msg):
        logger.warning(f"yt-dlp warning: {msg}")

    def error(self, msg):
        logger.error(f"yt-dlp error: {msg}")


class YoutubeDownloader:
    """YouTube to MP3 downloader using yt-dlp."""
    
    def __init__(self, download_folder: str = "downloads"):
        self.download_folder = download_folder
        Path(download_folder).mkdir(parents=True, exist_ok=True)
        logger.info(f"YoutubeDownloader initialized with folder: {download_folder}")
        
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Extract video metadata without downloading."""
        logger.info(f"Extracting video info for URL: {url}")
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                logger.debug("Calling yt_dlp.extract_info()")
                info = ydl.extract_info(url, download=False)
                
                # Handle playlists
                if 'entries' in info:
                    logger.debug("Playlist detected, using first entry")
                    video = info['entries'][0]
                else:
                    video = info
                
                result = {
                    'title': video.get('title', 'Unknown'),
                    'duration': video.get('duration', 0),
                    'thumbnail': video.get('thumbnail'),
                    'uploader': video.get('uploader', 'Unknown'),
                    'video_id': video.get('id'),
                    'webpage_url': video.get('webpage_url'),
                }
                logger.info(f"Successfully extracted info: title='{result['title']}', duration={result['duration']}s")
                return result
            except Exception as e:
                logger.error(f"Failed to extract video info: {str(e)}", exc_info=True)
                raise Exception(f"Failed to extract video info: {str(e)}")
    
    def download_mp3(self, url: str, output_format: str = "mp3") -> Tuple[str, float]:
        """
        Download video as MP3 or other audio format.
        
        Args:
            url: YouTube URL
            output_format: 'mp3' or 'ogg' or other audio format
            
        Returns:
            Tuple of (filename, size_in_mb)
        """
        logger.info(f"Starting MP3 download - URL: {url}, Format: {output_format}")
        logger_dl = DownloadLogger()
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'writethumbnail': True,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': output_format,
                    'preferredquality': '192',
                },
                {
                    'key': 'FFmpegMetadata',
                },
                {
                    'key': 'EmbedThumbnail',
                },
            ],
            'outtmpl': os.path.join(self.download_folder, '%(title)s-%(id)s.%(ext)s'),
            'logger': logger_dl,
            'quiet': False,
        }
        
        try:
            logger.debug("Creating YoutubeDL instance for download")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    logger.debug("Playlist detected, downloading first entry")
                    video = info['entries'][0]
                else:
                    video = info
                
                logger.debug(f"Downloading video: {video.get('title', 'Unknown')}")
                ydl.download([video['webpage_url']])
            
            # Get the downloaded file
            if logger_dl.last_file and os.path.exists(logger_dl.last_file):
                size_mb = os.path.getsize(logger_dl.last_file) / 1024 / 1024
                relative_path = os.path.relpath(logger_dl.last_file, self.download_folder)
                logger.info(f"MP3 download successful - File: {relative_path}, Size: {size_mb} MB")
                return relative_path, size_mb
            else:
                logger.error(f"Download completed but file not found. Last file: {logger_dl.last_file}")
                raise Exception("Download completed but file not found")
                
        except Exception as e:
            logger.error(f"MP3 download failed: {str(e)}", exc_info=True)
            raise Exception(f"Download failed: {str(e)}")
    
    def download_video(self, url: str) -> Tuple[str, float]:
        """Download video in best quality."""
        logger.info(f"Starting video download - URL: {url}")
        logger_dl = DownloadLogger()
        
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'writethumbnail': True,
            'postprocessors': [
                {
                    'key': 'FFmpegMetadata',
                },
            ],
            'outtmpl': os.path.join(self.download_folder, '%(title)s-%(id)s.%(ext)s'),
            'logger': logger_dl,
            'quiet': False,
        }
        
        try:
            logger.debug("Creating YoutubeDL instance for video download")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                if 'entries' in info:
                    logger.debug("Playlist detected, using first entry")
                    video = info['entries'][0]
                else:
                    video = info

                logger.debug(f"Downloaded video: {video.get('title', 'Unknown')}")

                filepath = None
                requested = video.get('requested_downloads') or []
                if requested:
                    filepath = requested[0].get('filepath') or requested[0].get('filename')

                if not filepath:
                    filepath = video.get('filepath') or video.get('filename')

                if not filepath:
                    try:
                        filepath = ydl.prepare_filename(video)
                    except Exception:
                        filepath = None

            if not filepath and logger_dl.last_file:
                filepath = logger_dl.last_file

            if filepath and os.path.exists(filepath):
                size_mb = os.path.getsize(filepath) / 1024 / 1024
                relative_path = os.path.relpath(filepath, self.download_folder)
                logger.info(f"Video download successful - File: {relative_path}, Size: {size_mb} MB")
                return relative_path, size_mb
            else:
                logger.error(f"Download completed but file not found. Last file: {logger_dl.last_file}")
                raise Exception("Download completed but file not found")

        except Exception as e:
            logger.error(f"Video download failed: {str(e)}", exc_info=True)
            raise Exception(f"Download failed: {str(e)}")
