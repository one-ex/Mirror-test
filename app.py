#!/usr/bin/env python3
"""
PixelDrain Mirror Service untuk Hugging Face Spaces
Dengan timeout 60 menit dan perilaku SAMA PERSIS dengan mirror-test.py
"""
import os
import logging
import time
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from urllib.parse import quote, urlparse

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfigurasi untuk HF Spaces - SAMA dengan mirror-test.py
API_KEY = os.getenv("PIXELDRAIN_API_KEY", "")
CHUNK_SIZE = 50 * 1024 * 1024  # 50MB - SAMA dengan mirror-test.py
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB max (batas HF Spaces)
TIMEOUT_LIMIT = 3000  # 50 menit untuk menjaga margin dari 60 menit

class HFMirrorService:
    def __init__(self):
        self.api_key = API_KEY
        self.session = requests.Session()
        # SAMA PERSIS dengan mirror-test.py
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0 Safari/537.36',
        })
        self.auth = HTTPBasicAuth('', self.api_key) if self.api_key else None
    
    def get_file_info(self, url: str):
        """Get file info dengan HEAD request - SAMA dengan mirror-test.py"""
        try:
            response = self.session.head(url, timeout=30, allow_redirects=True)
            file_size = int(response.headers.get('content-length', 0))
            
            # Ekstraksi filename SAMA dengan mirror-test.py
            final_url = response.url
            path = urlparse(final_url).path
            filename = os.path.basename(path.replace('/download', ''))
            if not filename:
                filename = "mirrored_file.zip"
            
            return {
                'size': file_size,
                'filename': filename,
                'accessible': True,
                'final_url': final_url
            }
        except Exception as e:
            logger.error(f"❌ Cannot access file: {str(e)}")
            return {'accessible': False, 'error': str(e)}
    
    def mirror_file(self, source_url: str):
        """Mirror file dengan perilaku SAMA PERSIS mirror-test.py"""
        start_time = time.time()
        
        try:
            # SAMA PERSIS dengan mirror-test.py
            logger.info(f"[*] Menghubungkan ke source...")
            
            with self.session.get(source_url, stream=True, allow_redirects=True) as download_response:
                download_response.raise_for_status()
                
                # Get file info SAMA dengan mirror-test.py
                file_info = self.get_file_info(source_url)
                if not file_info['accessible']:
                    return {'success': False, 'error': file_info.get('error', 'File not accessible')}
                
                # Validasi ukuran file
                if file_info['size'] > MAX_FILE_SIZE:
                    return {
                        'success': False, 
                        'error': f'File too large: {file_info["size"] / (1024*1024*1024):.2f}GB > {MAX_FILE_SIZE / (1024*1024*1024):.0f}GB limit'
                    }
                
                total_size = file_info['size']
                filename = file_info['filename']
                
                file_size_mb = total_size / (1024*1024) if total_size > 0 else 0
                logger.info(f"[*] Nama File : {filename}")
                logger.info(f"[*] Ukuran    : {file_size_mb:.2f} MB")
                logger.info(f"[*] Chunk Size: {CHUNK_SIZE / (1024*1024):.0f} MB")
                logger.info("-" * 50)
                
                # Generator dengan progress - SAMA PERSIS dengan mirror-test.py
                def generate_with_progress():
                    bytes_done = 0
                    start_dl_time = time.time()
                    
                    for chunk in download_response.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            yield chunk
                            bytes_done += len(chunk)
                            
                            # Hitung persentase dan kecepatan - SAMA PERSIS
                            if total_size > 0:
                                percent = (bytes_done / total_size) * 100
                                elapsed = time.time() - start_dl_time
                                speed = (bytes_done / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                                
                                # Progress display SAMA dengan mirror-test.py
                                logger.info(f"[>] Progress: {percent:.2f}% | Terkirim: {bytes_done/(1024*1024):.1f}MB | Speed: {speed:.2f} MB/s")
                
                # Upload ke PixelDrain - SAMA PERSIS dengan mirror-test.py
                upload_url = f"https://pixeldrain.com/api/file/{quote(filename)}"
                logger.info(f"[*] Uploading to: {upload_url}")
                
                upload_response = self.session.put(
                    upload_url,
                    data=generate_with_progress(),
                    auth=self.auth,
                    timeout=TIMEOUT_LIMIT
                )
                
                if upload_response.status_code in [200, 201]:
                    result = upload_response.json()
                    file_id = result.get('id', '')
                    elapsed_time = (time.time() - start_time) / 60
                    
                    logger.info(f"\n\n[V] BERHASIL!")
                    logger.info(f"[V] URL: https://pixeldrain.com/u/{file_id}")
                    logger.info(f"[V] Time: {elapsed_time:.1f} minutes")
                    
                    return {
                        'success': True,
                        'file_id': file_id,
                        'pixeldrain_url': f'https://pixeldrain.com/u/{file_id}',
                        'filename': filename,
                        'size': total_size,
                        'upload_time_minutes': elapsed_time
                    }
                else:
                    logger.error(f"\n[!] Gagal di PixelDrain: {upload_response.text}")
                    return {
                        'success': False, 
                        'error': f'Upload failed: {upload_response.status_code} - {upload_response.text}'
                    }

        except requests.exceptions.Timeout:
            elapsed = (time.time() - start_time) / 60
            return {
                'success': False, 
                'error': f'Operation timed out after {elapsed:.1f} minutes (60 min limit)'
            }
        except Exception as e:
            elapsed = (time.time() - start_time) / 60
            logger.error(f"\n[!] Terjadi kesalahan setelah {elapsed:.1f} menit: {str(e)}")
            return {'success': False, 'error': str(e)}

# Initialize service
mirror_service = HFMirrorService()

@app.route('/mirror', methods=['POST'])
def mirror():
    """Mirror endpoint dengan perilaku SAMA PERSIS mirror-test.py"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'Missing URL parameter'}), 400
        
        source_url = data['url'].strip()
        if not source_url.startswith(('http://', 'https://')):
            return jsonify({'error': 'Invalid URL format'}), 400
        
        logger.info(f"🚀 Starting mirror process for: {source_url}")
        result = mirror_service.mirror_file(source_url)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"❌ Endpoint error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'api_key_configured': bool(mirror_service.api_key),
        'max_file_size': f'{MAX_FILE_SIZE / (1024*1024*1024):.0f}GB',
        'timeout_limit': f'{TIMEOUT_LIMIT/60:.0f} minutes',
        'chunk_size': f'{CHUNK_SIZE / (1024*1024):.0f}MB',
        'behavior': 'Identical to mirror-test.py'
    })

@app.route('/info', methods=['GET'])
def info():
    """Info endpoint"""
    return jsonify({
        'service': 'PixelDrain Mirror for Hugging Face Spaces',
        'version': '3.0 - Identical to mirror-test.py',
        'features': [
            'Streaming upload/download (no local storage)',
            'Timeout handling (60 minutes)',
            'Large file support (2GB)',
            'Progress tracking (real-time)',
            'Identical behavior to successful mirror-test.py'
        ],
        'limits': {
            'max_file_size': f'{MAX_FILE_SIZE / (1024*1024*1024):.0f}GB',
            'timeout': f'{TIMEOUT_LIMIT/60:.0f} minutes',
            'chunk_size': f'{CHUNK_SIZE / (1024*1024):.0f}MB'
        },
        'compatibility': '100% identical to mirror-test.py'
    })

if __name__ == '__main__':
    # Port untuk Hugging Face Spaces
    port = int(os.environ.get('PORT', 7860))
    logger.info(f"🚀 Starting PixelDrain Mirror Service v3.0 on port {port}")
    logger.info(f"📊 Config: {MAX_FILE_SIZE/(1024*1024*1024):.0f}GB max, {TIMEOUT_LIMIT/60:.0f}min timeout")
    logger.info(f"✅ Behavior: 100% identical to mirror-test.py")
    app.run(host='0.0.0.0', port=port, debug=False)