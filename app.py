#!/usr/bin/env python3
"""
Smart Glasses Web Server
Flask application providing web interface for smart glasses camera system.
"""

import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
from arduino_camera import ESP32Camera

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None
    print("⚠️  Warning: GEMINI_API_KEY not found in .env file")

# Global camera instance
camera = ESP32Camera()
camera_running = False

class SmartGlassesSystem:
    def __init__(self):
        self.captures_dir = Path("captures")
        self.captures_dir.mkdir(exist_ok=True)
        self.chat_history = []
    
    def get_recent_images(self, limit=20):
        """Get most recent captured images"""
        images = []
        for img_path in sorted(self.captures_dir.glob("*.jpg"), key=os.path.getmtime, reverse=True):
            if len(images) >= limit:
                break
            images.append({
                'filename': img_path.name,
                'path': str(img_path),
                'timestamp': datetime.fromtimestamp(img_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'size': img_path.stat().st_size
            })
        return images
    
    def analyze_image_with_gemini(self, image_path, user_question=None):
        """Analyze image using Gemini Vision API"""
        if not model:
            return "Gemini API not configured. Please add GEMINI_API_KEY to .env file."
        
        try:
            # Read image
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
            
            # Prepare prompt
            if user_question:
                prompt = f"User question: {user_question}\n\nPlease analyze this image and answer the user's question. Be detailed and helpful."
            else:
                prompt = """Analyze this image captured by smart glasses. Describe:
1. What you see in the scene
2. Any people, objects, or activities
3. The environment/location
4. Anything notable or interesting
5. Context that might be useful for someone wearing smart glasses

Be concise but informative."""
            
            # Create image part
            image_part = {
                "mime_type": "image/jpeg",
                "data": img_data
            }
            
            # Generate response
            response = model.generate_content([prompt, image_part])
            return response.text
            
        except Exception as e:
            return f"Error analyzing image: {str(e)}"
    
    def chat_with_context(self, user_message, recent_images_count=5):
        """Chat with Gemini using context from recent images"""
        if not model:
            return "Gemini API not configured. Please add GEMINI_API_KEY to .env file."
        
        try:
            # Get recent images for context
            recent_images = self.get_recent_images(recent_images_count)
            
            # Build context prompt
            context_prompt = f"""You are an AI assistant for smart glasses. The user is asking: "{user_message}"

You have access to context from recent images captured by the smart glasses:
"""
            
            # Add image context
            for i, img in enumerate(recent_images[:3]):  # Use top 3 most recent
                context_prompt += f"\nImage {i+1} (captured at {img['timestamp']}): {img['filename']}\n"
            
            context_prompt += "\nPlease respond helpfully based on this context. If the question relates to recent visual information, reference what the smart glasses likely captured."
            
            # Generate response
            response = model.generate_content(context_prompt)
            
            # Store chat history
            self.chat_history.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'user_message': user_message,
                'ai_response': response.text
            })
            
            return response.text
            
        except Exception as e:
            return f"Error in chat: {str(e)}"

# Global system instance
glasses_system = SmartGlassesSystem()

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/api/images')
def get_images():
    """Get recent images"""
    images = glasses_system.get_recent_images()
    return jsonify(images)

@app.route('/api/image/<filename>')
def serve_image(filename):
    """Serve image file"""
    image_path = glasses_system.captures_dir / filename
    if image_path.exists():
        return send_file(image_path)
    return "Image not found", 404

@app.route('/api/analyze/<filename>', methods=['POST'])
def analyze_image(filename):
    """Analyze specific image"""
    image_path = glasses_system.captures_dir / filename
    if not image_path.exists():
        return jsonify({'error': 'Image not found'}), 404
    
    data = request.get_json()
    user_question = data.get('question') if data else None
    
    analysis = glasses_system.analyze_image_with_gemini(image_path, user_question)
    return jsonify({'analysis': analysis})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with AI assistant"""
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    response = glasses_system.chat_with_context(user_message)
    return jsonify({'response': response})

@app.route('/api/chat/history')
def chat_history():
    """Get chat history"""
    return jsonify(glasses_system.chat_history)

@app.route('/api/camera/start', methods=['POST'])
def start_camera():
    """Start camera capture"""
    global camera_running
    
    if camera_running:
        return jsonify({'message': 'Camera already running'}), 200
    
    try:
        camera.start_continuous_capture(interval=10.0)
        camera_running = True
        return jsonify({'message': 'Camera started successfully'})
    except Exception as e:
        return jsonify({'error': f'Failed to start camera: {str(e)}'}), 500

@app.route('/api/camera/stop', methods=['POST'])
def stop_camera():
    """Stop camera capture"""
    global camera_running
    
    try:
        camera.stop_continuous_capture()
        camera_running = False
        return jsonify({'message': 'Camera stopped successfully'})
    except Exception as e:
        return jsonify({'error': f'Failed to stop camera: {str(e)}'}), 500

@app.route('/api/camera/status')
def camera_status():
    """Get camera status"""
    return jsonify({
        'running': camera_running,
        'connected': camera.ser is not None
    })

@app.route('/api/camera/capture', methods=['POST'])
def capture_single():
    """Capture single image"""
    try:
        if not camera.ser:
            if not camera.connect():
                return jsonify({'error': 'Failed to connect to camera'}), 500
        
        image_path = camera.capture_single_image()
        if image_path:
            return jsonify({'message': 'Image captured', 'path': image_path})
        else:
            return jsonify({'error': 'Failed to capture image'}), 500
    except Exception as e:
        return jsonify({'error': f'Capture error: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting Smart Glasses Web Server...")
    print("📱 Access your smart glasses interface at: http://localhost:5000")
    print("🔍 Make sure your .env file contains: GEMINI_API_KEY=your_api_key")
    print("📸 Connect your ESP32 camera and use the web interface to start capturing")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        if camera_running:
            camera.stop_continuous_capture()
        camera.disconnect()
        print("✅ Server stopped")
