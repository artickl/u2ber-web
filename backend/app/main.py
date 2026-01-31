from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import os
from typing import Optional
import asyncio
import logging
from dotenv import load_dotenv
from .downloader import YoutubeDownloader

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="U2BER YouTube Downloader")

# Get configuration from environment variables
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER", "downloads")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Configure CORS based on environment
cors_origins = ["*"]
if ENVIRONMENT == "production":
    cors_origins = [FRONTEND_URL]
else:
    # Allow both localhost and 127.0.0.1 for development
    cors_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:8000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize downloader
downloader = YoutubeDownloader(download_folder=DOWNLOAD_FOLDER)


class DownloadRequest(BaseModel):
    url: str
    format: str = "mp3"  # mp3, ogg, etc.


class VideoInfo(BaseModel):
    title: str
    duration: int
    thumbnail: Optional[str] = None
    uploader: str
    video_id: str


@app.get("/api")
async def root():
    return {
        "message": "U2BER YouTube Downloader API",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "api_base_url": API_BASE_URL,
        "endpoints": {
            "info": "GET /api/info?url=<youtube_url>",
            "download": "POST /api/download",
            "downloads": "GET /api/downloads"
        }
    }


@app.get("/api/info", response_model=VideoInfo)
async def get_video_info(url: str):
    """Get video metadata without downloading."""
    logger.info(f"Getting video info for URL: {url}")
    try:
        info = downloader.get_video_info(url)
        logger.debug(f"Successfully retrieved video info: {info}")
        return VideoInfo(**info)
    except Exception as e:
        logger.error(f"Error getting video info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/download")
async def download_audio(request: DownloadRequest, background_tasks: BackgroundTasks):
    """Download YouTube audio in specified format."""
    logger.info(f"Download request received - URL: {request.url}, Format: {request.format}")
    try:
        logger.debug(f"Starting download process for format: {request.format}")
        if request.format.lower() == "video":
            logger.debug("Downloading as video")
            filename, size = downloader.download_video(request.url)
        else:
            logger.debug(f"Downloading as audio format: {request.format}")
            filename, size = downloader.download_mp3(request.url, request.format)
        
        logger.info(f"Download successful - Filename: {filename}, Size: {size} MB")
        return {
            "status": "success",
            "filename": filename,
            "size_mb": round(size, 2),
            "download_url": f"/api/file/{filename}"
        }
    except Exception as e:
        logger.error(f"Download failed - Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/file/{file_path:path}")
async def download_file(file_path: str):
    """Download the prepared file."""
    logger.debug(f"Download file requested: {file_path}")
    full_path = os.path.join(DOWNLOAD_FOLDER, file_path)
    
    # Security: prevent directory traversal
    if not os.path.abspath(full_path).startswith(os.path.abspath(DOWNLOAD_FOLDER)):
        logger.warning(f"Directory traversal attempt detected for file: {file_path}")
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not os.path.exists(full_path):
        logger.warning(f"File not found: {full_path}")
        raise HTTPException(status_code=404, detail="File not found")
    
    logger.info(f"Serving file: {file_path}")
    return FileResponse(
        full_path,
        filename=os.path.basename(full_path),
        media_type="application/octet-stream"
    )


@app.get("/api/downloads")
async def list_downloads():
    """List all downloaded files."""
    logger.debug("Listing downloads")
    try:
        files = []
        for filename in os.listdir(DOWNLOAD_FOLDER):
            filepath = os.path.join(DOWNLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                size_mb = os.path.getsize(filepath) / 1024 / 1024
                files.append({
                    "filename": filename,
                    "size_mb": round(size_mb, 2),
                    "download_url": f"/api/file/{filename}"
                })
        logger.debug(f"Found {len(files)} files")
        return {"files": files}
    except Exception as e:
        logger.error(f"Error listing downloads: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/file/{file_path:path}")
async def delete_file(file_path: str):
    """Delete a downloaded file."""
    logger.info(f"Delete file requested: {file_path}")
    full_path = os.path.join(DOWNLOAD_FOLDER, file_path)
    
    # Security: prevent directory traversal
    if not os.path.abspath(full_path).startswith(os.path.abspath(DOWNLOAD_FOLDER)):
        logger.warning(f"Directory traversal attempt detected for deletion: {file_path}")
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not os.path.exists(full_path):
        logger.warning(f"File not found for deletion: {full_path}")
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        os.remove(full_path)
        logger.info(f"File successfully deleted: {file_path}")
        return {"status": "deleted", "filename": file_path}
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
