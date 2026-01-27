import React, { useState, useRef, useEffect } from 'react'
import './App.css'
import { initGA, trackEvent } from './analytics'

function App() {
  const [url, setUrl] = useState('')
  const [format, setFormat] = useState('mp3')
  const [videoInfo, setVideoInfo] = useState(null)
  const [loading, setLoading] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [downloads, setDownloads] = useState([])
  const [showDownloads, setShowDownloads] = useState(false)

  // Get API base URL from environment variables, fallback to localhost
  const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

  // Initialize Google Analytics on mount
  useEffect(() => {
    initGA()
  }, [])

  const fetchVideoInfo = async () => {
    if (!url.trim()) {
      setError('Please enter a YouTube URL')
      return
    }

    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const response = await fetch(`${API_BASE}/api/info?url=${encodeURIComponent(url)}`)
      if (!response.ok) {
        throw new Error('Failed to fetch video info')
      }
      const data = await response.json()
      setVideoInfo(data)
    } catch (err) {
      setError(err.message || 'Failed to load video information')
      setVideoInfo(null)
    } finally {
      setLoading(false)
    }
  }

  const downloadFile = async () => {
    if (!url.trim()) {
      setError('Please enter a YouTube URL')
      return
    }

    setDownloading(true)
    setError('')
    setSuccess('')

    try {
      const response = await fetch(`${API_BASE}/api/download`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url,
          format: format,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Download failed')
      }

      const data = await response.json()
      setSuccess(`✓ Downloaded: ${data.filename} (${data.size_mb} MB)`)
      
      // Track download event in Google Analytics
      trackEvent('download', 'Video', format, data.size_mb)
      
      setUrl('')
      setVideoInfo(null)
      fetchDownloads()
    } catch (err) {
      setError(err.message || 'Download failed')
    } finally {
      setDownloading(false)
    }
  }

  const fetchDownloads = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/downloads`)
      if (!response.ok) throw new Error('Failed to fetch downloads')
      const data = await response.json()
      setDownloads(data.files || [])
    } catch (err) {
      console.error('Failed to fetch downloads:', err)
    }
  }

  const deleteFile = async (filename) => {
    try {
      const response = await fetch(`${API_BASE}/api/file/${filename}`, {
        method: 'DELETE',
      })
      if (!response.ok) throw new Error('Failed to delete file')
      fetchDownloads()
    } catch (err) {
      setError(err.message || 'Failed to delete file')
    }
  }

  React.useEffect(() => {
    if (showDownloads) {
      fetchDownloads()
    }
  }, [showDownloads])

  return (
    <div className="app">
      <header className="header">
        <img src="u2ber-transparent-logo.svg" alt="U2BER logo with stylized text and YouTube-themed design elements on transparent background" className="logo" />
        <h1>
          U2BER - YouTube Downloader
        </h1>
        <p>Convert YouTube videos to audio and download them for offline listening</p>
      </header>

      <main className="container">
        <div className="card">
          <div className="input-group">
            <input
              type="text"
              placeholder="Paste YouTube URL here..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') fetchVideoInfo()
              }}
              className="url-input"
            />
            <button onClick={fetchVideoInfo} disabled={loading} className="btn btn-secondary">
              {loading ? 'Loading...' : 'Get Info'}
            </button>
          </div>

          {videoInfo && (
            <div className="video-info">
              {videoInfo.thumbnail && (
                <img src={videoInfo.thumbnail} alt={`Video thumbnail for ${videoInfo.title} by ${videoInfo.uploader}`} className="thumbnail" />
              )}
              <div className="info-details">
                <h3>{videoInfo.title}</h3>
                <p>by {videoInfo.uploader}</p>
                <p className="duration">Duration: {Math.floor(videoInfo.duration / 60)}m {videoInfo.duration % 60}s</p>
              </div>
            </div>
          )}

          <div className="format-selector">
            <label>Output Format:</label>
            <select value={format} onChange={(e) => setFormat(e.target.value)}>
              <option value="mp3">MP3 (Audio)</option>
              <option value="ogg">OGG (Audio)</option>
              <option value="wav">WAV (Audio)</option>
              <option value="video">Video (MP4)</option>
            </select>
          </div>

          {error && <div className="error">{error}</div>}
          {success && <div className="success">{success}</div>}

          <button
            onClick={downloadFile}
            disabled={!videoInfo || downloading}
            className="btn btn-primary btn-large"
          >
            {downloading ? 'Downloading...' : '⬇️ Download'}
          </button>
        </div>

        <button
          onClick={() => setShowDownloads(!showDownloads)}
          className="btn btn-secondary"
        >
          {showDownloads ? 'Hide' : 'Show'} Downloads ({downloads.length})
        </button>

        {showDownloads && (
          <div className="downloads-list">
            <h2>Recent Downloads</h2>
            {downloads.length === 0 ? (
              <p className="empty">No downloads yet</p>
            ) : (
              <ul>
                {downloads.map((file) => (
                  <li key={file.filename} className="download-item">
                    <div className="file-info">
                      <span className="filename">{file.filename}</span>
                      <span className="size">{file.size_mb} MB</span>
                    </div>
                    <div className="file-actions">
                      <a href={file.download_url} download className="btn btn-small">
                        ⬇️ Download
                      </a>
                      <button
                        onClick={() => deleteFile(file.filename)}
                        className="btn btn-small btn-danger"
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </main>

      <footer className="footer">
        <p>
            Created by <a href="https://artem.zavyalov.site" target="_blank">Artem Zavyalov</a>
            <span className="divider"> • </span>
            <a href="https://github.com/artickl/u2ber-web" target="_blank">View on GitHub</a>
        </p>
        <p className="clone-command">
            Clone the repository: <code>git clone https://github.com/artickl/u2ber-web</code>
        </p>
      </footer>
    </div>
  )
}

export default App
