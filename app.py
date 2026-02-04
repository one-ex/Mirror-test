import os
import requests
import time
from requests.auth import HTTPBasicAuth
from urllib.parse import quote, urlparse
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration - Updated to match mirror-test.py (10MB chunks)
DEFAULT_CHUNK_SIZE = 100 * 1024 * 1024  # 10MB chunks (same as mirror-test.py)
MAX_RETRIES = 3
TIMEOUT = 300  # 5 minutes timeout

class PixelDrainMirror:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('PIXELDRAIN_API_KEY')
        self.session = requests.Session()
        if self.api_key:
            self.session.auth = HTTPBasicAuth('', self.api_key)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0 Safari/537.36',
        })

    def extract_filename(self, url):
        """Extract filename from URL with proper handling"""
        try:
            parsed = urlparse(url)
            path = parsed.path
            filename = os.path.basename(path.replace('/download', ''))
            
            # Remove common query parameters that might be in path
            if '?' in filename:
                filename = filename.split('?')[0]
            
            return filename if filename else "uploaded_file.zip"
        except Exception:
            return "uploaded_file.zip"

    def mirror_with_progress(self, source_url, progress_callback=None):
        """Mirror file from source to PixelDrain with progress tracking - Updated logic from mirror-test.py"""
        
        # Use 10MB chunk size like in mirror-test.py
        CHUNK_SIZE = 10 * 1024 * 1024
        
        try:
            print(f"[*] Connecting to source...")
            
            # Start streaming download and upload in one go (like mirror-test.py)
            with self.session.get(source_url, stream=True, allow_redirects=True, timeout=TIMEOUT) as source_response:
                source_response.raise_for_status()
                
                # Extract filename using the same logic as mirror-test.py
                final_url = source_response.url
                path = urlparse(final_url).path
                filename = os.path.basename(path.replace('/download', ''))
                if not filename:
                    filename = "mirrored_file.zip"
                
                total_size = int(source_response.headers.get('content-length', 0))
                
                print(f"[*] Filename: {filename}")
                print(f"[*] Size: {total_size / (1024*1024):.2f} MB")
                print(f"[*] Chunk Size: {CHUNK_SIZE / (1024*1024)} MB")
                print("-" * 50)
                
                if progress_callback:
                    progress_callback({
                        'status': 'starting',
                        'filename': filename,
                        'total_size': total_size,
                        'message': f'Starting mirror for {filename}'
                    })
                
                # Generate stream with progress (mirror-test.py logic)
                def generate_with_progress():
                    bytes_done = 0
                    start_time = time.time()
                    
                    for chunk in source_response.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            yield chunk
                            bytes_done += len(chunk)
                            
                            # Calculate percentage and speed
                            percent = (bytes_done / total_size) * 100 if total_size > 0 else 0
                            elapsed = time.time() - start_time
                            speed = (bytes_done / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                            
                            # Show progress (like mirror-test.py)
                            progress_msg = f"[>] Progress: {percent:.2f}% | Sent: {bytes_done/(1024*1024):.1f}MB | Speed: {speed:.2f} MB/s"
                            print(progress_msg, end='\r', flush=True)
                            
                            if progress_callback:
                                progress_callback({
                                    'status': 'transferring',
                                    'progress': percent,
                                    'speed_mbps': speed,
                                    'transferred': bytes_done,
                                    'total': total_size,
                                    'message': progress_msg
                                })
                
                # Upload to PixelDrain
                upload_url = f"https://pixeldrain.com/api/file/{quote(filename)}"
                
                upload_response = self.session.put(
                    upload_url,
                    data=generate_with_progress(),
                    timeout=TIMEOUT
                )
                
                print()  # New line after progress
                
                if upload_response.status_code in [200, 201]:
                    result = upload_response.json()
                    
                    success_msg = f"[V] BERHASIL! URL: https://pixeldrain.com/u/{result['id']}"
                    print(f"\n{success_msg}")
                    
                    if progress_callback:
                        progress_callback({
                            'status': 'completed',
                            'file_id': result['id'],
                            'url': f"https://pixeldrain.com/u/{result['id']}",
                            'size': result.get('size', 0),
                            'message': success_msg
                        })
                    
                    return {
                        'success': True,
                        'file_id': result['id'],
                        'url': f"https://pixeldrain.com/u/{result['id']}",
                        'filename': filename,
                        'size': result.get('size', 0)
                    }
                else:
                    raise Exception(f"Upload failed: {upload_response.status_code} - {upload_response.text}")
                    
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            print(f"\n[!] Network error: {str(e)}")
            if progress_callback:
                progress_callback({
                    'status': 'error',
                    'error': error_msg,
                    'message': error_msg
                })
            return {'success': False, 'error': error_msg}
            
        except Exception as e:
            error_msg = f"Mirror failed: {str(e)}"
            print(f"\n[!] Error: {str(e)}")
            if progress_callback:
                progress_callback({
                    'status': 'error',
                    'error': error_msg,
                    'message': error_msg
                })
            return {'success': False, 'error': error_msg}

# Initialize mirror service
mirror_service = PixelDrainMirror()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'pixeldrain-mirror'})

@app.route('/mirror', methods=['POST'])
def mirror_file():
    """Main mirror endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        source_url = data['url'].strip()
        if not source_url:
            return jsonify({'error': 'URL cannot be empty'}), 400
        
        # Optional API key override
        api_key = data.get('api_key')
        if api_key:
            mirror_service.session.auth = HTTPBasicAuth('', api_key)
        
        def progress_callback(progress_data):
            # In a real deployment, you might want to use WebSocket or SSE
            # For now, we'll just log it
            app.logger.info(f"Progress: {progress_data.get('message', '')}")
        
        # Start mirroring
        result = mirror_service.mirror_with_progress(source_url, progress_callback)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        app.logger.error(f"Endpoint error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/mirror/simple', methods=['POST'])
def simple_mirror():
    """Simple mirror without progress tracking"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        source_url = data['url'].strip()
        
        # Optional API key override
        api_key = data.get('api_key')
        if api_key:
            mirror_service.session.auth = HTTPBasicAuth('', api_key)
        
        result = mirror_service.mirror_with_progress(source_url)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        app.logger.error(f"Simple mirror error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"[INFO] Starting PixelDrain Mirror Service on port {port}")
    print(f"[INFO] Debug mode: {debug}")
    print(f"[INFO] API Key configured: {'Yes' if os.getenv('PIXELDRAIN_API_KEY') else 'No'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)