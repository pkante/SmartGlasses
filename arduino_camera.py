#!/usr/bin/env python3
"""
Smart Glasses Camera Module
Handles continuous image capture from ESP32 camera for smart glasses system.
"""

import time
import serial
import struct
import pathlib
import threading
from datetime import datetime

class ESP32Camera:
    def __init__(self, port="/dev/cu.usbmodem2101", baud=115200, timeout=1.0):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.ser = None
        self.running = False
        self.capture_thread = None
        self.captures_dir = pathlib.Path("captures")
        self.captures_dir.mkdir(exist_ok=True)
        
    def connect(self):
        """Establish connection to ESP32 camera"""
        try:
            print(f"🔌 Connecting to ESP32 on {self.port}...")
            self.ser = serial.Serial(self.port, self.baud, timeout=self.timeout)
            
            # Give ESP32 time to reboot after opening port
            time.sleep(2.0)
            self.ser.reset_input_buffer()
            
            # Read any boot/ready messages
            print("📡 Reading ESP32 boot messages...")
            t0 = time.time()
            while time.time() - t0 < 5.0:
                line = self.ser.readline()
                if not line:
                    break
                try:
                    message = line.decode(errors="ignore").strip()
                    if message:
                        print(f"ESP32: {message}")
                except:
                    pass
            
            print("✅ ESP32 camera connected successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to ESP32: {e}")
            return False
    
    def capture_single_image(self):
        """Capture a single image from ESP32"""
        if not self.ser:
            print("❌ ESP32 not connected")
            return None
            
        try:
            # Send trigger to capture
            self.ser.write(b"x")
            
            # Find sync pattern 0xAA 0x55
            buf = bytearray()
            deadline = time.time() + 20.0
            found = False
            
            while time.time() < deadline:
                chunk = self.ser.read(1024)
                if chunk:
                    buf += chunk
                    # Search for sync in buffer
                    i = buf.find(b"\xAA\x55")
                    if i != -1:
                        # Ensure we have the 4-byte length after sync
                        while len(buf) < i + 2 + 4:
                            more = self.ser.read(1024)
                            if more:
                                buf += more
                            elif time.time() >= deadline:
                                break
                        
                        if len(buf) >= i + 6:
                            length = struct.unpack("<I", buf[i+2:i+6])[0]
                            print(f"📸 Sync found. JPEG length: {length} bytes")
                            
                            # Consume header
                            buf = buf[i+6:]
                            
                            # Read remaining image bytes
                            while len(buf) < length and time.time() < deadline:
                                more = self.ser.read(length - len(buf))
                                if more:
                                    buf += more
                            
                            if len(buf) >= length:
                                img = bytes(buf[:length])
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"capture_{timestamp}.jpg"
                                filepath = self.captures_dir / filename
                                filepath.write_bytes(img)
                                print(f"💾 Saved {filepath} (size: {len(img)} bytes)")
                                found = True
                                return str(filepath)
                        break
            
            if not found:
                print("⚠️  No image received within timeout")
                return None
                
        except Exception as e:
            print(f"❌ Error capturing image: {e}")
            return None
    
    def start_continuous_capture(self, interval=10.0):
        """Start continuous image capture in background thread for smart glasses"""
        if self.running:
            print("⚠️  Continuous capture already running")
            return
            
        if not self.connect():
            return
            
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, args=(interval,))
        self.capture_thread.daemon = True
        self.capture_thread.start()
        print(f"🎥 Started smart glasses capture (every {interval}s)")
    
    def _capture_loop(self, interval):
        """Internal capture loop"""
        while self.running:
            try:
                self.capture_single_image()
                time.sleep(interval)
            except Exception as e:
                print(f"❌ Error in capture loop: {e}")
                time.sleep(interval)
    
    def stop_continuous_capture(self):
        """Stop continuous image capture"""
        self.running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=5.0)
        print("🛑 Continuous capture stopped")
    
    def disconnect(self):
        """Disconnect from ESP32"""
        self.stop_continuous_capture()
        if self.ser:
            self.ser.close()
            self.ser = None
        print("🔌 ESP32 disconnected")

def main():
    """Test the ESP32 camera module"""
    camera = ESP32Camera()
    
    try:
        # Test single capture
        if camera.connect():
            print("Testing single capture...")
            result = camera.capture_single_image()
            if result:
                print(f"✅ Single capture successful: {result}")
            else:
                print("❌ Single capture failed")
        
        # Test continuous capture for a short time
        print("\nTesting continuous capture for 30 seconds...")
        camera.start_continuous_capture(interval=10.0)
        time.sleep(30)
        camera.stop_continuous_capture()
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    finally:
        camera.disconnect()

if __name__ == "__main__":
    main()
