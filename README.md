# Smart Glasses System

A web-based smart glasses interface that captures images from an ESP32 camera and provides AI-powered image analysis and chat capabilities using Google's Gemini AI.

## 🚀 Features

- **📸 Continuous Image Capture**: ESP32 camera captures images every 10 seconds
- **🖼️ Web Image Gallery**: Browse all captured images in a responsive web interface
- **🤖 AI Image Analysis**: Analyze images using Google Gemini Vision API
- **💬 Chat Interface**: Interactive chat with AI assistant about your captured images
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **⚡ Real-time Updates**: Auto-refreshing image gallery and live camera status

## 🏗️ Architecture

```
📦 Smart Glasses System
├── 📸 arduino_camera.py     # ESP32 camera communication
├── 🌐 app.py               # Flask web server
├── 📁 templates/
│   └── index.html          # Main web interface
├── 📁 static/
│   ├── css/style.css       # Custom styles
│   └── js/app.js          # Frontend JavaScript
└── 📁 captures/           # Captured images directory
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your Gemini API key
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### 2. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

### 3. ESP32 Camera Setup

- Connect your ESP32 camera via USB
- Default port: `/dev/cu.usbmodem101` (macOS) or `/dev/ttyUSB0` (Linux)
- Update the port in `arduino_camera.py` if needed

### 4. Run the System

```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

## 📱 Web Interface

### Camera Controls
- **Start/Stop Camera**: Begin continuous 10-second interval capture
- **Capture Now**: Take a single image immediately
- **Camera Status**: Real-time connection and capture status

### Image Gallery
- View all captured images in a responsive grid
- Click any image to open detailed analysis modal
- Auto-refreshes when camera is running

### AI Chat
- Ask questions about your captured images
- Get contextual responses based on recent captures
- Persistent chat history

### Image Analysis
- Click any image to analyze it with Gemini AI
- Ask specific questions about individual images
- Get detailed descriptions of scenes, objects, and activities

## 🔧 Configuration

### Camera Settings

Edit `arduino_camera.py` to adjust:
- Serial port (default: `/dev/cu.usbmodem101`)
- Baud rate (default: `115200`)
- Capture interval (default: `10.0` seconds)

### Web Server Settings

Edit `app.py` to modify:
- Server port (default: `5000`)
- Host binding (default: `0.0.0.0`)
- Image storage location

## 📋 API Endpoints

### Camera Control
- `POST /api/camera/start` - Start continuous capture
- `POST /api/camera/stop` - Stop capture
- `POST /api/camera/capture` - Single capture
- `GET /api/camera/status` - Camera status

### Images
- `GET /api/images` - List recent images
- `GET /api/image/<filename>` - Serve image file
- `POST /api/analyze/<filename>` - Analyze specific image

### Chat
- `POST /api/chat` - Send chat message
- `GET /api/chat/history` - Get chat history

## 🛠️ Development

### Project Structure
```
📁 smart-glasses/
├── arduino_camera.py      # ESP32 communication module
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── captures/             # Image storage (auto-created)
├── templates/
│   └── index.html        # Web interface template
└── static/
    ├── css/style.css     # Custom styles
    └── js/app.js         # Frontend JavaScript
```

### Adding Features

1. **New API Endpoints**: Add routes in `app.py`
2. **Frontend Features**: Modify `templates/index.html` and `static/js/app.js`
3. **Camera Features**: Extend `arduino_camera.py`
4. **Styling**: Update `static/css/style.css`

## 🔍 Troubleshooting

### Camera Issues
```bash
# Check available ports (macOS)
ls /dev/cu.*

# Check available ports (Linux)
ls /dev/ttyUSB*

# Test camera connection
python -c "from arduino_camera import ESP32Camera; cam = ESP32Camera(); print('Connected:' if cam.connect() else 'Failed')"
```

### Gemini API Issues
- Verify your API key in `.env`
- Check your Google Cloud billing is enabled
- Ensure Gemini API is enabled in your project

### Web Server Issues
- Check if port 5000 is available
- Try running with `python app.py --host 0.0.0.0 --port 8000`
- Check firewall settings for local network access

## 📊 Usage Examples

### Smart Glasses Use Cases

1. **Daily Life Assistant**
   - "What am I looking at?"
   - "Is this safe to eat?"
   - "What's the weather outside based on what you see?"

2. **Learning Aid**
   - "Explain what's in this book page"
   - "Help me identify this plant/animal"
   - "What architectural style is this building?"

3. **Navigation Help**
   - "What street signs do you see?"
   - "Describe the path ahead"
   - "Are there any obstacles I should know about?"

4. **Social Assistance**
   - "Describe the people in this room"
   - "What's happening in this scene?"
   - "Help me read this text"

## 📄 License

This project is for educational and research purposes. Ensure compliance with local privacy laws when using camera and AI features.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the console logs in your browser
3. Check the Flask server output for errors
4. Ensure all dependencies are properly installed