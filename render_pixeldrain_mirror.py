#!/usr/bin/env python3
"""
PixelDrain Mirror Service for Render.com
Mirrors files from any URL to PixelDrain with streaming upload
"""

import os
import time
import logging
from typing import Dict, Any, Optional
from urllib.parse import quote, urlparse
import requests
from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class PixelDrainMirrorService:
    def __init__(self):
        self.api_key = os.getenv('PIXELDRAIN_API_KEY', '')
        self.default_chunk_size = int(os.getenv('CHUNK_SIZE_MB', '50')) * 1024 * 1024
        self.max_file_size = int(os.getenv('MAX_FILE_SIZE_MB', '5000')) * 1024 * 1024
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0 Safari/537.36',
        })
        
    def extract_filename(self, response: requests.Response) -> str:
        """Extract filename from response headers or URL"""
        # Try Content-Disposition header first
        content_disposition = response.headers.get('content-disposition', '')
        if content_disposition:
            import re
            filename_match = re.search(r'filename[*]?=(?:UTF-8\')?([^;]+)', content_disposition)
            if filename_match:
                filename = filename_match.group(1).strip('"\'')
                if filename:
                    return filename
        
        # Fallback to URL path
        final_url = response.url
        path = urlparse(final_url).path
        filename = os.path.basename(path.replace('/download', ''))
        
        # Clean up filename
        filename = filename.strip()
        if not filename or '.' not in filename:
            filename = f"mirrored_file_{int(time.time())}.bin"
            
        return filename
    
    def test_pixeldrain_connection(self) -> bool:
        """Test if we can reach PixelDrain from current environment"""
        try:
            # Test basic connectivity
            response = self.session.get('https://pixeldrain.com', timeout=10)
            if response.status_code == 200:
                logger.info("✅ PixelDrain connectivity test passed")
                return True
            else:
                logger.error(f"❌ PixelDrain connectivity test failed: Status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Cannot reach PixelDrain: {str(e)}")
            return False
    
    def mirror_file(self, source_url: str, chunk_size: int = None) -> Dict[str, Any]:
        """Mirror file from source URL to PixelDrain"""
        if not chunk_size:
            chunk_size = self.default_chunk_size
            
        if not self.api_key:
            raise ValueError("PIXELDRAIN_API_KEY is required")
            
        logger.info(f"Starting mirror from: {source_url}")
        
        # Test PixelDrain connectivity first
        if not self.test_pixeldrain_connection():
            raise Exception("Cannot reach PixelDrain. This might be a network restriction in the current environment.")
        
        try:
            # Connect to source
            with self.session.get(source_url, stream=True, allow_redirects=True, timeout=30) as response:
                response.raise_for_status()
                
                # Extract file info
                filename = self.extract_filename(response)
                total_size = int(response.headers.get('content-length', 0))
                
                # Validate file size
                if total_size > self.max_file_size:
                    raise ValueError(f"File size {total_size/(1024*1024):.1f}MB exceeds maximum {self.max_file_size/(1024*1024):.1f}MB")
                
                logger.info(f"File: {filename} | Size: {total_size/(1024*1024):.2f}MB | Chunk: {chunk_size/(1024*1024):.1f}MB")
                
                # Progress tracking generator
                def generate_with_progress():
                    bytes_done = 0
                    start_time = time.time()
                    last_progress = 0
                    
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            yield chunk
                            bytes_done += len(chunk)
                            
                            # Calculate progress
                            if total_size > 0:
                                progress = int((bytes_done / total_size) * 100)
                                elapsed = time.time() - start_time
                                speed = (bytes_done / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                                
                                # Log progress every 10% or every 50MB
                                if progress >= last_progress + 10 or bytes_done - (last_progress * total_size / 100) > 50 * 1024 * 1024:
                                    last_progress = progress
                                    logger.info(f"Progress: {progress}% | Sent: {bytes_done/(1024*1024):.1f}MB | Speed: {speed:.2f} MB/s")
                
                # Upload to PixelDrain
                upload_url = f"https://pixeldrain.com/api/file/{quote(filename)}"
                auth = requests.auth.HTTPBasicAuth('', self.api_key)
                
                logger.info("Uploading to PixelDrain...")
                upload_response = self.session.put(
                    upload_url,
                    data=generate_with_progress(),
                    auth=auth,
                    timeout=None  # No timeout for large uploads
                )
                
                if upload_response.status_code in [200, 201]:
                    result = upload_response.json()
                    file_id = result.get('id')
                    file_url = f"https://pixeldrain.com/u/{file_id}"
                    
                    logger.info(f"✅ Upload successful! URL: {file_url}")
                    
                    return {
                        'success': True,
                        'file_id': file_id,
                        'url': file_url,
                        'filename': filename,
                        'size': total_size,
                        'message': 'File mirrored successfully'
                    }
                else:
                    error_msg = f"PixelDrain upload failed: {upload_response.status_code} - {upload_response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error: {str(e)}")
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Mirror failed: {str(e)}")
            raise

# Initialize service
mirror_service = PixelDrainMirrorService()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'pixeldrain-mirror',
        'timestamp': int(time.time())
    })

@app.route('/test-connection', methods=['GET'])
def test_connection():
    """Test connection to PixelDrain"""
    try:
        connectivity_test = mirror_service.test_pixeldrain_connection()
        return jsonify({
            'pixeldrain_reachable': connectivity_test,
            'api_key_configured': bool(mirror_service.api_key),
            'message': 'Connection test completed'
        })
    except Exception as e:
        return jsonify({
            'pixeldrain_reachable': False,
            'api_key_configured': bool(mirror_service.api_key),
            'error': str(e)
        }), 500

@app.route('/mirror', methods=['POST'])
def mirror_endpoint():
    """Main mirror endpoint"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            raise BadRequest("Missing 'url' in request body")
        
        source_url = data['url'].strip()
        if not source_url:
            raise BadRequest("URL cannot be empty")
        
        # Optional chunk size
        chunk_size = None
        if 'chunk_size_mb' in data:
            try:
                chunk_size = int(data['chunk_size_mb']) * 1024 * 1024
            except ValueError:
                raise BadRequest("chunk_size_mb must be a valid integer")
        
        logger.info(f"Mirror request received for: {source_url}")
        result = mirror_service.mirror_file(source_url, chunk_size)
        
        return jsonify(result)
        
    except BadRequest as e:
        logger.error(f"Bad request: {str(e)}")
        return jsonify({'error': str(e.description)}), 400
    except Exception as e:
        logger.error(f"Mirror error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with usage info"""
    return jsonify({
        'service': 'PixelDrain Mirror Service',
        'version': '1.0.0',
        'endpoints': {
            'POST /mirror': 'Mirror a file to PixelDrain',
            'GET /health': 'Health check'
        },
        'usage': {
            'method': 'POST',
            'endpoint': '/mirror',
            'body': {
                'url': 'https://example.com/file.zip',
                'chunk_size_mb': 50  # optional
            }
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    
    # Check for API key
    if not mirror_service.api_key:
        logger.error("⚠️  PIXELDRAIN_API_KEY not set! Set it in Render.com environment variables.")
    else:
        logger.info(f"✅ Service configured with API key: {mirror_service.api_key[:8]}...")
    
    logger.info(f"🚀 Starting PixelDrain Mirror Service on port {port}")
    
    # Use Waitress for production
    from waitress import serve
    serve(app, host='0.0.0.0', port=port)