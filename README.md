---
title: PixelDrain Mirror Service
emoji: 📁
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 7860
---

# PixelDrain Mirror Service 🚀

Mirror files from any URL to PixelDrain with **60-minute timeout** support for large files!

## ✨ New Features (v2.0)

- **🕐 60-Minute Timeout**: Support for very large files
- **📦 2GB File Size**: Maximum file size limit
- **⚡ Progress Tracking**: Real-time upload progress
- **📊 Speed Monitoring**: Track transfer speed
- **⏱️ Time Estimation**: Estimated completion time

## 🚀 Features

- **Streaming Upload/Download**: Memory efficient for any file size
- **Large File Support**: Handle files up to 2GB
- **Progress Tracking**: Real-time logging every 30 seconds
- **Speed Monitoring**: MB/s transfer rate display
- **Error Handling**: Comprehensive error messages
- **Timeout Handling**: Full 60-minute request timeout

## 📋 API Usage

### Mirror a File
```bash
curl -X POST https://your-space.hf.space/mirror \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/large-file.zip"}'
```

### Health Check
```bash
curl https://your-space.hf.space/health
```

### Service Info
```bash
curl https://your-space.hf.space/info
```

## ⚙️ Configuration

Add `PIXELDRAIN_API_KEY` in Space settings for authenticated uploads.

## 📝 Limits

- **Max File Size**: 2GB
- **Timeout**: 60 minutes
- **Supported URLs**: HTTP/HTTPS direct links
- **Chunk Size**: 50MB for optimal performance

## 🔄 Response Format

### Success Response
```json
{
  "success": true,
  "file_id": "abc123def",
  "pixeldrain_url": "https://pixeldrain.com/u/abc123def",
  "filename": "large-file.zip",
  "size": 1073741824,
  "upload_time_minutes": 12.5
}
```

### Error Response
```json
{
  "success": false,
  "error": "File too large: 2.5GB > 2.0GB limit"
}
```

## 🧪 Test Examples

### Small File (Quick Test)
```bash
curl -X POST https://your-space.hf.space/mirror \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"}'
```

### Medium File (100MB)
```bash
curl -X POST https://your-space.hf.space/mirror \
  -H "Content-Type: application/json" \
  -d '{"url": "https://speed.hetzner.de/100MB.bin"}'
```

### Large File (1GB) - Will take ~10 minutes
```bash
curl -X POST https://your-space.hf.space/mirror \
  -H "Content-Type: application/json" \
  -d '{"url": "https://speed.hetzner.de/1GB.bin"}'
```

## 📊 Progress Monitoring

The service will log progress every 30 seconds:
```
📊 Progress: 15.3% | Speed: 8.5 MB/s
📊 Progress: 30.7% | Speed: 8.2 MB/s
📊 Progress: 46.1% | Speed: 8.7 MB/s
```

## 🔧 Troubleshooting

- **"Operation timed out"**: File terlalu besar atau koneksi lambat (>60 menit)
- **"File not accessible"**: URL tidak valid atau membutuhkan autentikasi
- **"Network error"**: PixelDrain atau source tidak dapat diakses
- **Slow speed**: Tergantung koneksi antara HF Spaces → Source → PixelDrain

## 💡 Tips for Large Files

1. **Test dengan file kecil dulu** untuk memastikan semua bekerja
2. **Gunakan URL dengan speed tinggi** (seperti speedtest.net)
3. **Monitor logs** untuk melihat progress 30-detik
4. **Siapkan waktu**: 1GB butuh ~10 menit dengan kecepatan 10MB/s

---

**Note**: Dengan timeout 60 menit, Anda bisa mirror file hingga **2GB**! 🎉