# PixelDrain Mirror Service

A web service for mirroring files from any URL to PixelDrain with streaming and progress tracking.

## Features

- ✅ Direct streaming from source to PixelDrain (no local storage)
- ✅ Progress tracking with speed monitoring
- ✅ Error handling and retry logic
- ✅ RESTful API endpoints
- ✅ Health check endpoint
- ✅ Configurable chunk sizes
- ✅ Support for both authenticated and guest uploads

## Quick Start

### Local Development

1. Clone and setup:
```bash
git clone <your-repo>
cd pixeldrain-mirror
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your PixelDrain API key (optional)
```

3. Run locally:
```bash
python app.py
```

### Deploy to Render.com

1. Fork this repository
2. Connect to Render.com:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Use these settings:
     - **Name**: pixeldrain-mirror
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
     - **Instance Type**: Free tier (upgrade later if needed)

3. Set environment variables in Render:
   - `PIXELDRAIN_API_KEY`: Your PixelDrain API key (optional)
   - `DEBUG`: Set to `False` for production
   - `PORT`: 8080 (Render will override this)

## API Usage

### Health Check
```bash
GET /health
```

### Mirror File (Simple)
```bash
POST /mirror/simple
Content-Type: application/json

{
  "url": "https://example.com/file.zip"
}
```

### Mirror File (With Progress)
```bash
POST /mirror
Content-Type: application/json

{
  "url": "https://example.com/file.zip",
  "api_key": "your-api-key"  // Optional, overrides default
}
```

### Response Format
Success:
```json
{
  "success": true,
  "file_id": "abc123",
  "url": "https://pixeldrain.com/u/abc123",
  "filename": "file.zip",
  "size": 1048576
}
```

Error:
```json
{
  "success": false,
  "error": "Error message"
}
```

## Configuration

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `PIXELDRAIN_API_KEY` | Your PixelDrain API key | None (guest upload) |
| `DEBUG` | Enable debug mode | `False` |
| `PORT` | Port to run on | `8080` |
| `CHUNK_SIZE_MB` | Upload chunk size in MB | `5` |
| `UPLOAD_TIMEOUT` | Upload timeout in seconds | `300` |

## Limitations

- **No resume capability**: Unlike Google Drive resumable upload, if connection fails, must restart from beginning
- **Timeout risk**: Very large files (>5GB) may timeout
- **Single stream**: Cannot upload chunks independently
- **Rate limiting**: Guest uploads have stricter limits

## Error Handling

The service handles various error scenarios:
- Network connectivity issues
- Invalid URLs
- PixelDrain API errors
- Timeout conditions
- File size limitations

## Production Considerations

For production deployment:
1. **Use a production WSGI server** (gunicorn is configured)
2. **Set up monitoring** with the `/health` endpoint
3. **Configure proper logging** levels
4. **Use environment variables** for sensitive data
5. **Consider rate limiting** for your endpoints
6. **Set up error alerting**

## PixelDrain API Key (Optional)

While not required, having a PixelDrain API key provides:
- Higher rate limits
- File management capabilities
- Better reliability

Get your API key at: https://pixeldrain.com/user/api_keys