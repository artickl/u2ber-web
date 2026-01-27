#!/usr/bin/python3
"""Refactored YouTube downloader module for web service."""

from __future__ import unicode_literals
import yt_dlp
import os
from pathlib import Path
from typing import Tuple, Dict, Any


class DownloadLogger:
    """Custom logger for yt-dlp to capture download progress."""
    
    def __init__(self):
        self.last_file = None
        
    def debug(self, msg):
        lookupmessage = "[ExtractAudio] Destination: "
        if msg.startswith(lookupmessage):
            self.last_file = msg[len(lookupmessage):]

    def warning(self, msg):
        pass

    def error(self, msg):
        print(f"ERROR: {msg}")


class YoutubeDownloader:
    """YouTube to MP3 downloader using yt-dlp."""
    
    def __init__(self, download_folder: str = "downloads"):
        self.download_folder = download_folder
        Path(download_folder).mkdir(parents=True, exist_ok=True)
        
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Extract video metadata without downloading."""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                
                # Handle playlists
                if 'entries' in info:
                    video = info['entries'][0]
                else:
                    video = info
                
                return {
                    'title': video.get('title', 'Unknown'),
                    'duration': video.get('duration', 0),
                    'thumbnail': video.get('thumbnail'),
                    'uploader': video.get('uploader', 'Unknown'),
                    'video_id': video.get('id'),
                    'webpage_url': video.get('webpage_url'),
                }
            except Exception as e:
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
        logger = DownloadLogger()
        
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
            'logger': logger,
            'quiet': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    video = info['entries'][0]
                else:
                    video = info
                
                ydl.download([video['webpage_url']])
            
            # Get the downloaded file
            if logger.last_file and os.path.exists(logger.last_file):
                size_mb = os.path.getsize(logger.last_file) / 1024 / 1024
                # Return relative path for serving
                relative_path = os.path.relpath(logger.last_file, self.download_folder)
                return relative_path, size_mb
            else:
                raise Exception("Download completed but file not found")
                
        except Exception as e:
            raise Exception(f"Download failed: {str(e)}")
    
    def download_video(self, url: str) -> Tuple[str, float]:
        """Download video in best quality."""
        logger = DownloadLogger()
        
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'writethumbnail': True,
            'postprocessors': [
                {
                    'key': 'FFmpegMetadata',
                },
            ],
            'outtmpl': os.path.join(self.download_folder, '%(title)s-%(id)s.%(ext)s'),
            'logger': logger,
            'quiet': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    video = info['entries'][0]
                else:
                    video = info
                
                ydl.download([video['webpage_url']])
            
            if logger.last_file and os.path.exists(logger.last_file):
                size_mb = os.path.getsize(logger.last_file) / 1024 / 1024
                relative_path = os.path.relpath(logger.last_file, self.download_folder)
                return relative_path, size_mb
            else:
                raise Exception("Download completed but file not found")
                
        except Exception as e:
            raise Exception(f"Download failed: {str(e)}")
