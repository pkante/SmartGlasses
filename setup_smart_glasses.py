#!/usr/bin/env python3
"""
Smart Glasses System Setup Script
Sets up the environment and checks configuration for the smart glasses system.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.7+"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_path = Path(".env")
    if env_path.exists():
        print("✅ .env file already exists")
        return True
    
    print("\n🔑 Creating .env file...")
    api_key = input("Enter your Gemini API key (or press Enter to skip): ").strip()
    
    if api_key:
        env_content = f"GEMINI_API_KEY={api_key}\n"
        env_path.write_text(env_content)
        print("✅ .env file created with API key")
    else:
        env_content = "# Add your Gemini API key here\n# GEMINI_API_KEY=your_api_key_here\n"
        env_path.write_text(env_content)
        print("⚠️  .env file created but you'll need to add your API key manually")
    
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    directories = ["captures", "static/css", "static/js", "templates"]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ All directories created")
    return True

def check_serial_ports():
    """Check for available serial ports"""
    print("\n🔌 Checking for available serial ports...")
    
    # Check for common ESP32 ports
    common_ports = [
        "/dev/cu.usbmodem101",  # macOS
        "/dev/cu.usbmodem2101", # macOS alternative
        "/dev/ttyUSB0",         # Linux
        "/dev/ttyUSB1",         # Linux alternative
        "COM3",                 # Windows
        "COM4",                 # Windows alternative
    ]
    
    available_ports = []
    for port in common_ports:
        if os.path.exists(port):
            available_ports.append(port)
    
    if available_ports:
        print(f"✅ Found potential ESP32 ports: {', '.join(available_ports)}")
        print("💡 Update arduino_camera.py if your ESP32 uses a different port")
    else:
        print("⚠️  No common ESP32 ports found")
        print("💡 Connect your ESP32 and check the port manually")
    
    return True

def run_test():
    """Run a quick test of the system"""
    print("\n🧪 Running system test...")
    
    try:
        # Test imports
        from arduino_camera import ESP32Camera
        from app import app
        print("✅ All modules import successfully")
        
        # Test camera initialization
        camera = ESP32Camera()
        print("✅ Camera module initializes correctly")
        
        # Test Flask app
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Web server responds correctly")
            else:
                print("⚠️  Web server returned unexpected status")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Test warning: {e}")
        return True

def print_next_steps():
    """Print instructions for next steps"""
    print("\n" + "="*60)
    print("🎉 SMART GLASSES SETUP COMPLETE!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("1. Connect your ESP32 camera via USB")
    print("2. If you haven't already, add your Gemini API key to .env:")
    print("   GEMINI_API_KEY=your_api_key_here")
    print("3. Start the system:")
    print("   python app.py")
    print("4. Open your browser to: http://localhost:5000")
    print("\n🔗 Get Gemini API Key:")
    print("   https://makersuite.google.com/app/apikey")
    print("\n💡 Tips:")
    print("   - Use the web interface to start/stop camera")
    print("   - Click images to analyze them with AI")
    print("   - Chat with the AI about what you're seeing")
    print("   - Images are saved in the 'captures' folder")

def main():
    """Main setup function"""
    print("🚀 Smart Glasses System Setup")
    print("="*40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create directories
    if not create_directories():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Check serial ports
    check_serial_ports()
    
    # Run tests
    if not run_test():
        print("\n⚠️  Some tests failed, but you can still try running the system")
    
    # Print next steps
    print_next_steps()
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
    else:
        print("\n✅ Setup completed successfully!")
