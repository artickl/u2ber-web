# U2BER YouTube Downloader - Web Version

A web application for downloading YouTube videos as MP3 or other audio formats, with future support for video downloads and audio editing tools.

## Project Structure

```txt
/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── main.py   # FastAPI application
│   │   ├── downloader.py  # YouTube downloader logic
│   │   └── __init__.py
│   ├── .env.example # should be copied as .env.local and adjusted for hosting purposes
│   ├── requirements.txt
│   ├── run.sh
│   ├── Dockerfile
│   └── downloads/    # Downloaded files directory
├── frontend/         # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.css
│   ├── .env.example # should be copied as .env.local and adjusted for hosting purposes
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── Dockerfile
│   └── .gitignore
├── docker-compose.yml
├── ENV_GUIDE.md
└── README.md
```

## Quick Start

### Environment Setup

The project uses environment files for configuration. Each environment has its own settings:

**Available environments:**

- `.env.local` - Local development (default, not in git)
- `.env.production` - Production settings example

#### Backend Environment Variables

Copy `.env.example` to `.env.local` and adjust:

```bash
cd backend
cp .env.example .env.local
```

Edit `.env.local`:

```env
# For localhost testing (default)
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
ENVIRONMENT=development
```

#### Frontend Environment Variables

Copy `.env.example` to `.env.local`:

```bash
cd frontend
cp .env.example .env.local
```

Edit `.env.local`:

```env
# For localhost testing (default)
VITE_API_BASE=http://localhost:8000
VITE_ENVIRONMENT=development
```

### Option 1: Local Development (Recommended for Development)

#### Backend Setup

```bash
cd web/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy environment file (already set for localhost)
cp .env.example .env.local

# Run
chmod +x run.sh
./run.sh
```

The backend will run on `http://localhost:8000` and automatically load settings from `.env.local`

#### Frontend Setup (in a new terminal)

```bash
cd web/frontend
npm install

# Copy environment file (already set for localhost)
cp .env.example .env.local

# Run
chmod +x run.sh
./run.sh
```

The frontend will run on `http://localhost:5173` and use the API at `http://localhost:8000`

### Option 2: Docker Compose (Recommended for Deployment)

```bash
cd web
docker-compose up
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

For production deployment with your domain, create `.env` files before building.

**backend/.env:**

```env
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=https://********/api
FRONTEND_URL=https://********
ENVIRONMENT=production
```

**frontend/.env:**

```env
VITE_API_BASE=https://********/api
VITE_ENVIRONMENT=production
```

Then build and deploy:

```bash
docker-compose up --build
```

## Environment Configuration

### How It Works

1. **Local Development**: `.env.local` files are automatically loaded and excluded from git
2. **Production**: Set environment variables when deploying (Docker, systemd, etc.)
3. **No hardcoding**: All URLs are configurable without code changes

### Switching Between Environments

**To test with localhost:**

```bash
# backend/.env.local
VITE_API_BASE=http://localhost:8000
```

Just restart the development servers and changes take effect immediately!

## Features

### Current ✅

- Download YouTube videos as MP3
- Get video metadata (title, duration, thumbnail, uploader)
- Support for multiple audio formats (MP3, OGG, WAV)
- Video download option
- View all downloads
- Delete downloaded files
- Clean, responsive UI
- Local file serving

### Coming Soon 🚀

- Audio trimmer (remove seconds from start/end)
- EXIF editor (edit music metadata - artist, song name, etc.)
- Thumbnail editor
- Download history with timestamps
- Batch downloads
- Quality/bitrate selection
- Playlist support

## API Endpoints

### Get Video Info

```TXT
GET /api/info?url=<youtube_url>
```

Response:

```json
{
  "title": "Video Title",
  "duration": 300,
  "thumbnail": "https://...",
  "uploader": "Channel Name",
  "video_id": "dQw4w9WgXcQ"
}
```

### Download Audio/Video

```TXT
POST /api/download
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=...",
  "format": "mp3"
}
```

### List Downloads

```TXT
GET /api/downloads
```

### Download File

```TXT
GET /api/file/<filename>
```

### Delete File

```TXT
DELETE /api/file/<filename>
```

## System Requirements

- Python 3.11+
- Node.js 18+
- FFmpeg (required by yt-dlp for audio conversion)

### Install FFmpeg

**Ubuntu/Debian:**

```bash
sudo apt-get install ffmpeg
```

**macOS:**

```bash
brew install ffmpeg
```

**Windows:**
Download from [https://ffmpeg.org/download.html]

## Environment Variables

Create `.env` file in backend directory if needed:

```env
# Backend
DOWNLOAD_FOLDER=downloads
MAX_DOWNLOAD_SIZE_MB=500
```

## Troubleshooting

### FFmpeg not found

Make sure FFmpeg is installed and in your PATH:

```bash
ffmpeg -version
```

### Port already in use

Change ports in `docker-compose.yml` or use:

```bash
lsof -ti :8000  # Find process on port 8000
kill -9 <PID>   # Kill the process
```

### CORS errors

The frontend is configured to proxy API requests through Vite's dev server. In production, ensure CORS headers are properly configured.

## Development Tips

- Backend auto-reloads on file changes (development mode)
- Frontend hot-reloads with Vite
- Check backend logs: [http://localhost:8000/docs] (Swagger UI)
- API responses include helpful error messages

## Future Enhancements

- [ ] Audio trimmer tool
- [ ] EXIF/metadata editor
- [ ] Thumbnail customizer
- [ ] Playlist batch download
- [ ] Quality selection
- [ ] Download queue management
- [ ] User authentication
- [ ] Database for tracking downloads
- [ ] Email notifications for completed downloads

## License

MIT
