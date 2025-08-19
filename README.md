# Smart Glasses System

A simple web-based smart glasses interface that captures images from an ESP32 camera and provides AI-powered image analysis and chat capabilities using Google's Gemini AI.

## 🔧 Hardware Used

**Camera**: [Seeed Studio XIAO ESP32S3 Sense](https://www.amazon.com/Seeed-Studio-XIAO-ESP32-Sense/dp/B0C69FFVHH?th=1) - A tiny ESP32-S3 development board with camera

**Glasses**: [EYLRIM Thick Square Frame Blue Light Glasses](https://www.amazon.com/dp/B0BWNWRFKY?ref=ppx_yo2ov_dt_b_fed_asin_title) - Non-prescription computer glasses for mounting the camera

## 🚀 Features

- **📸 Continuous Image Capture**: ESP32 camera captures images every 10 seconds
- **🖼️ Web Image Gallery**: Browse all captured images in a responsive web interface
- **🤖 AI Image Analysis**: Analyze images using Google Gemini Vision API
- **💬 Chat Interface**: Interactive chat with AI assistant about your captured images
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **⚡ Real-time Updates**: Auto-refreshing image gallery and live camera status


```

## Quick Start

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

### 3. Arduino/ESP32 Setup

First, you need to flash the firmware to your XIAO ESP32S3:

1. Open the `firmware` folder and open the `.ino` file in the Arduino IDE.

2. If you don't have the Arduino IDE installed, download and install it from the [official website](https://www.arduino.cc/en/software).
   - Alternatively, follow the steps in the firmware readme to build using arduino-cli

3. Set up the Arduino IDE for the XIAO ESP32S3 board:
   - **Add ESP32 board package**: Go to File > Preferences, and fill "Additional Boards Manager URLs" with: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - **Install ESP32 boards**: Go to Tools > Board > Boards Manager..., search for "esp32", select the latest version and install it.

4. **Select your board and port**:
   - On top of the Arduino IDE, select the port (likely COM3 or higher on Windows, or `/dev/cu.usbmodem101` on macOS)
   - Search for "xiao" in the development board list and select **XIAO_ESP32S3**

5. **Important**: Before flashing, go to the "Tools" dropdown in Arduino IDE and set **"PSRAM: OPI PSRAM"**

6. Upload the firmware to the XIAO ESP32S3 board.

7. Connect your ESP32 camera via USB and update the port in `arduino_camera.py` if needed

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


### Camera Settings

Edit `arduino_camera.py` to adjust:
- Serial port (default: `/dev/cu.usbmodem101`)
- Baud rate (default: `115200`)
- Capture interval (default: `10.0` seconds)



---

That's it! You've got yourself a smart glasses system. Have fun experimenting with it! 🤓

**Note**: Be mindful of privacy when using the camera and AI features.
