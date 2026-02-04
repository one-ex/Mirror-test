# PixelDrain Mirror Service

A production-ready web service that mirrors files from any URL to PixelDrain with streaming upload. Built with Flask and optimized for Render.com deployment.

## Features

- ✅ **Streaming Upload**: Memory-efficient file mirroring with chunk-based processing
- ✅ **Progress Tracking**: Real-time upload progress with speed calculation
- ✅ **REST API**: Simple HTTP endpoints for file mirroring
- ✅ **Error Handling**: Comprehensive error handling and validation
- ✅ **Production Ready**: Built with Waitress WSGI server for production use
- ✅ **Configurable**: Environment variables for chunk size, max file size, etc.

## Quick Start

### 1. Local Development

```bash
# Clone and setup
git clone <your-repo>
cd pixeldrain-mirror

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your PixelDrain API key

# Run locally
python render_pixeldrain_mirror.py
```

### 2. Test Locally

```bash
# Health check
curl http://localhost:5000/health

# Mirror a file
curl -X POST http://localhost:5000/mirror \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"}'
```

## Render.com Deployment

### 1. Create Render Account

1. Go to [render.com](https://render.com) and sign up
2. Connect your GitHub/GitLab account

### 2. Create New Web Service

1. Click "New" → "Web Service"
2. Connect your repository
3. Use these settings:
   - **Name**: `pixeldrain-mirror`
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python render_pixeldrain_mirror.py`

### 3. Configure Environment Variables

In Render dashboard, add these environment variables:

```env
PIXELDRAIN_API_KEY=your_pixeldrain_api_key_here
CHUNK_SIZE_MB=50
MAX_FILE_SIZE_MB=5000
PORT=5000
```

### 4. Deploy

Click "Create Web Service" and wait for deployment to complete.

## API Documentation

### Endpoints

#### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "pixeldrain-mirror",
  "timestamp": 1234567890
}
```

#### `POST /mirror`
Mirror a file to PixelDrain

**Request:**
```json
{
  "url": "https://example.com/file.zip",
  "chunk_size_mb": 50  // optional, default: 50
}
```

**Response (Success):**
```json
{
  "success": true,
  "file_id": "abc123",
  "url": "https://pixeldrain.com/u/abc123",
  "filename": "file.zip",
  "size": 10485760,
  "message": "File mirrored successfully"
}
```

**Response (Error):**
```json
{
  "error": "Error message here"
}
```

## Testing After Deployment

### 1. Health Check

```bash
# Replace with your actual Render URL
curl https://your-app-name.onrender.com/health
```

### 2. Mirror Test File

```bash
# Small test file (fast)
curl -X POST https://your-app-name.onrender.com/mirror \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"}'

# Medium test file
curl -X POST https://your-app-name.onrender.com/mirror \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/git/git/archive/refs/tags/v2.34.0.zip"}'

# Large test file (will take time)
curl -X POST https://your-app-name.onrender.com/mirror \
  -H "Content-Type: application/json" \
  -d '{"url": "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US"}'
```

### 3. Check Logs

In Render dashboard:
1. Go to your service
2. Click "Logs" tab
3. Monitor real-time logs

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PIXELDRAIN_API_KEY` | *required* | Your PixelDrain API key |
| `CHUNK_SIZE_MB` | 50 | Chunk size for streaming (MB) |
| `MAX_FILE_SIZE_MB` | 5000 | Maximum file size allowed (MB) |
| `PORT` | 5000 | Server port |

### Getting PixelDrain API Key

1. Go to [pixeldrain.com](https://pixeldrain.com)
2. Create account and login
3. Go to [API Keys page](https://pixeldrain.com/user/api_keys)
4. Generate new API key

## Troubleshooting

### Common Issues

1. **"PIXELDRAIN_API_KEY not set"**
   - Solution: Set the API key in Render environment variables

2. **"File size exceeds maximum"**
   - Solution: Increase `MAX_FILE_SIZE_MB` or use smaller files

3. **"Network error"**
   - Solution: Check source URL accessibility, try different URLs

4. **Upload timeout**
   - Solution: Large files take time, check logs for progress

### Debug Mode

Set `FLASK_ENV=development` for detailed logging.

## Security Notes

- API keys are stored in environment variables (never in code)
- Service validates URLs and file sizes
- No persistent storage - files go directly to PixelDrain
- Use HTTPS endpoints only

## Performance Tips

- **Chunk Size**: 50MB default works well for most files
- **Large Files**: Consider increasing chunk size to 100-200MB
- **Network**: Deploy in region closest to your users
- **Monitoring**: Use Render logs to monitor performance

## Support

- Check logs in Render dashboard
- Test with different file sizes and sources
- Monitor API rate limits on PixelDrain