# YouTube WAV Downloader

A simple web application for downloading YouTube videos as WAV files via y2down.cc.

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

### Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python api_server.py`
   - **Environment Variables**:
     - `PORT`: (auto-set by Render)
     - `HOST`: `0.0.0.0`

### Railway

1. Create a new project on Railway
2. Connect your GitHub repository
3. Railway will auto-detect Python and install dependencies
4. Set `HOST=0.0.0.0` in environment variables

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

