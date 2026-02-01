#!/usr/bin/env python3
"""
YouTube WAV Downloader Web App
Simple web application for downloading YouTube videos as WAV files via y2down.cc
No authentication required
"""

from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import logging
import os
import sys
from pathlib import Path

# Get the directory where this script is located and ensure it's in the path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# Ensure we import from the current directory, not from youtube_pipeline
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Import downloader module from current directory
from downloader import get_download_url, stream_download

# Log to confirm we're using the correct module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"Using downloader module from: {BASE_DIR}/downloader.py")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='/static')
CORS(app)

# Configuration
PORT = int(os.getenv('PORT', 5000))
HOST = os.getenv('HOST', '0.0.0.0')


@app.route('/')
def index():
    """Serve the main HTML page."""
    response = send_from_directory(BASE_DIR, 'index.html')
    # Add cache-busting headers to prevent browser from caching old version
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files explicitly."""
    response = send_from_directory(STATIC_DIR, filename)
    # Add cache-busting headers for static files
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'youtube-wav-downloader'})


@app.route('/api/status', methods=['GET'])
def status():
    """Get API status."""
    return jsonify({
        'status': 'running',
        'service': 'youtube-wav-downloader'
    })


@app.route('/api/download', methods=['POST'])
def download():
    """Download YouTube video as WAV via y2down.cc."""
    try:
        data = request.get_json()
        
        if not data or 'youtube_url' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing "youtube_url" in request body'
            }), 400
        
        youtube_url = data.get('youtube_url', '').strip()
        
        if not youtube_url:
            return jsonify({
                'success': False,
                'error': 'YouTube URL cannot be empty'
            }), 400
        
        if not (youtube_url.startswith('http://') or youtube_url.startswith('https://')):
            return jsonify({
                'success': False,
                'error': 'Invalid URL format'
            }), 400
        
        logger.info(f"Processing download request for: {youtube_url}")
        
        # Get download URL from y2down.cc (NOT downloaderto.com)
        logger.info("Calling get_download_url from y2down.cc downloader module")
        download_url, video_title = get_download_url(youtube_url)
        
        if not download_url:
            logger.error("Failed to get download URL from y2down.cc")
            return jsonify({
                'success': False,
                'error': 'Could not get download URL from y2down.cc. The service may be unavailable or the video may not be accessible.'
            }), 500
        
        # Determine filename
        if video_title:
            import re
            safe_title = re.sub(r'[^\w\s-]', '', video_title)
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            filename = f"{safe_title}.wav"
        else:
            filename = "video.wav"
        
        logger.info(f"Streaming download: {filename} from {download_url}")
        
        # Stream the file to the client
        def generate():
            try:
                for chunk in stream_download(download_url):
                    yield chunk
            except Exception as e:
                logger.error(f"Error streaming download: {e}")
                raise
        
        response = Response(
            generate(),
            mimetype='audio/wav',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'audio/wav'
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing download request: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Error processing download: {str(e)}'
        }), 500


if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    
    logger.info(f"Starting YouTube WAV Downloader on {HOST}:{PORT}")
    logger.info(f"Web interface available at http://{HOST}:{PORT}")
    
    app.run(host=HOST, port=PORT, debug=False)

