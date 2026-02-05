import requests
import os
import time
from requests.auth import HTTPBasicAuth
from urllib.parse import quote, urlparse

def mirror_sourceforge_to_pixeldrain(url, api_key):
    # Pengaturan Chunk Size 10MB
    CHUNK_SIZE = 50 * 1024 * 1024 
    
    session = requests.Session()
    auth = HTTPBasicAuth('', api_key)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0 Safari/537.36',
    })

    print(f"[*] Menghubungkan ke Sourceforge...")
    try:
        with session.get(url, stream=True, allow_redirects=True) as sf_response:
            sf_response.raise_for_status()
            
            # Ekstraksi Nama File
            final_url = sf_response.url
            path = urlparse(final_url).path
            filename = os.path.basename(path.replace('/download', ''))
            if not filename: filename = "mirrored_file.zip"

            total_size = int(sf_response.headers.get('content-length', 0))
            
            print(f"[*] Nama File : {filename}")
            print(f"[*] Ukuran    : {total_size / (1024*1024):.2f} MB")
            print(f"[*] Chunk Size: 10 MB")
            print("-" * 50)

            # Logika Progress Mirroring
            def generate_with_progress():
                bytes_done = 0
                start_time = time.time()
                
                for chunk in sf_response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        yield chunk
                        bytes_done += len(chunk)
                        
                        # Hitung persentase dan kecepatan
                        percent = (bytes_done / total_size) * 100
                        elapsed = time.time() - start_time
                        speed = (bytes_done / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                        
                        # Tampilkan Log (r untuk menimpa baris yang sama)
                        print(f"[>] Progress: {percent:.2f}% | Terkirim: {bytes_done/(1024*1024):.1f}MB | Speed: {speed:.2f} MB/s", end='\r')

            # Kirim data ke PixelDrain
            upload_url = f"https://pixeldrain.com/api/file/{quote(filename)}"
            pd_response = session.put(
                upload_url,
                data=generate_with_progress(),
                auth=auth
            )

            if pd_response.status_code in [200, 201]:
                result = pd_response.json()
                print(f"\n\n[V] BERHASIL!")
                print(f"[V] URL: https://pixeldrain.com/u/{result['id']}")
            else:
                print(f"\n[!] Gagal di PixelDrain: {pd_response.text}")

    except Exception as e:
        print(f"\n[!] Terjadi kesalahan: {str(e)}")

# --- CONFIG ---
MY_API_KEY = "91468e11-cb6e-42a4-8320-93ad9cce62b6"
SF_URL = "https://excellmedia.dl.sourceforge.net/project/alphadroid-project/marble/AlphaDroid-16-20260122_172732-vanilla-marble-v4.2.zip?viasf=1"

mirror_sourceforge_to_pixeldrain(SF_URL, MY_API_KEY)