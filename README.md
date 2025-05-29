# Twitter Video Downloader

A modern web application for downloading Twitter/X videos with a clean UI inspired by x-downloader.com.

## 🚀 Features

- **Fast & Free**: Download Twitter videos instantly without registration
- **Multiple Formats**: Support for MP4 video and MP3 audio downloads  
- **Quality Options**: Choose from available video quality options
- **Modern UI**: Clean, responsive design with dark theme
- **Cross-Platform**: Works on desktop and mobile devices
- **No Software Required**: Browser-based tool, no downloads needed

## 🌐 Live Demo

Visit the live demo: [https://www.pullvideo.com/]

## 📋 Quick Start

1. **Visit the website**
2. **Paste Twitter video URL** in the input field
3. **Select format** (MP4 or MP3)
4. **Click Download** and choose your preferred quality
5. **Download** starts automatically in a new tab

## 🛠 Technical Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python with yt-dlp
- **Deployment**: Vercel Serverless Functions
- **API**: RESTful API with CORS support

## 🚀 Deployment on Vercel

This project is optimized for Vercel deployment with the following structure:

```
xvideodownloader/
├── api/                    # Vercel Serverless Functions
│   ├── download.py        # Main download API endpoint
│   └── health.py         # Health check endpoint  
├── static/               # Static frontend files
│   ├── index.html       # Main webpage
│   └── styles.css       # Stylesheet
├── vercel.json          # Vercel configuration (optimized)
└── requirements.txt     # Python dependencies
```

### Automatic Deployment

1. **Fork this repository** to your GitHub account
2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your forked repository
   - Click "Deploy"

3. **Configuration**: The project includes an optimized `vercel.json` that:
   - Automatically recognizes Python functions in `/api/` directory
   - Routes static files correctly
   - Handles CORS headers
   - No conflicting builds/functions configuration

### Manual Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

## 🔧 Local Development

```bash
# Clone the repository
git clone https://github.com/your-username/xvideodownloader.git
cd xvideodownloader

# Install dependencies
pip install -r requirements.txt

# Run development server
PORT=8000 python3 run.py

# Open browser
open http://localhost:8000
```

## 📚 API Documentation

### POST /api/download

Extract video information and download URLs.

**Request:**
```json
{
  "url": "https://twitter.com/username/status/123456789",
  "format": "mp4"
}
```

**Response:**
```json
{
  "title": "Video Title",
  "author": "@username", 
  "duration": "02:30",
  "thumbnail": "https://...",
  "formats": [
    {
      "quality": "1080p HD",
      "url": "https://...",
      "ext": "mp4",
      "filesize": "15.2 MB",
      "filename": "video.mp4"
    }
  ]
}
```

### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "platform": "vercel"
}
```

## 🔄 Recent Optimizations for Vercel

- ✅ **Removed conflicting builds/functions configuration**
- ✅ **Migrated from Flask to BaseHTTPRequestHandler** for better serverless compatibility  
- ✅ **Simplified dependency management** (removed Flask, Flask-CORS, Werkzeug)
- ✅ **Added proper CORS headers** in function responses
- ✅ **Used relative API paths** instead of hardcoded localhost URLs
- ✅ **Optimized vercel.json** according to Vercel best practices

## 🛡 Legal & Privacy

- **Privacy First**: No data storage, no tracking
- **Legal Use**: Respect copyright laws and Twitter's terms of service
- **Open Source**: MIT License - use responsibly

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/xvideodownloader/issues)
- **Email**: support@yoursite.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Disclaimer**: This tool is for downloading videos you own or have permission to download. Please respect copyright laws and platform terms of service. 