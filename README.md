# YouTube WAV Downloader

A simple web application for downloading YouTube videos as WAV files via y2down.cc.

## ⚠️ Status

**This is a working iteration as of February 2, 2026.** The application successfully downloads YouTube videos as WAV files via y2down.cc integration using Selenium automation.

## Features

- 🎵 Download YouTube videos as WAV files
- 🌐 Simple web interface
- 🚀 No authentication required
- ⚡ Fast downloads via y2down.cc

## Setup

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/cookie444/ytPipelineV3.git
cd ytPipelineV3
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python api_server.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## Requirements

- Python 3.11+
- Chrome/Chromium browser (for Selenium)
- ChromeDriver (automatically managed by webdriver-manager)

## Deployment

### Render (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository: `cookie444/ytPipelineV3`
4. Render will automatically detect the `render.yaml` file
5. Click "Apply" to deploy

The app will be live at a `*.onrender.com` URL.

### Railway

1. Go to [Railway](https://railway.app/)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select `cookie444/ytPipelineV3`
4. Railway will auto-detect Python and deploy
5. Set `HOST=0.0.0.0` in environment variables

### Other Platforms

The application is a standard Flask app and can be deployed to any platform that supports Python:
- Heroku
- AWS Elastic Beanstalk
- Google Cloud Run
- Azure App Service
- DigitalOcean App Platform

## Project Structure

```
YTpipeline v3/
├── api_server.py          # Flask backend server
├── downloader.py          # y2down.cc integration module
├── index.html             # Web interface
├── requirements.txt       # Python dependencies
├── static/
│   ├── script.js          # Frontend JavaScript
│   └── style.css          # Styling
└── test_downloadsample.py # Original Selenium test script
```

## How It Works

1. User enters a YouTube URL in the web interface
2. Backend uses Selenium to automate y2down.cc
3. Selects WAV format and submits the URL
4. Extracts the download URL
5. Streams the WAV file to the user's browser

## License

MIT

