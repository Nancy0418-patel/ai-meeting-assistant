#!/usr/bin/env python3
"""
Quick test script for Gemini Speech-to-Text integration
"""

import os
import sys
import tempfile
import wave

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from services.speech_to_text import SpeechToTextService
    print("✅ Speech-to-Text service imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_gemini_integration():
    """Test Gemini speech-to-text integration"""
    print("\n🎯 Testing Gemini Speech-to-Text Integration")
    print("=" * 50)
    
    # Initialize service
    stt = SpeechToTextService()
    
    # Check API key
    if stt.gemini_api_key:
        print("✅ Gemini API key found")
    else:
        print("⚠️  Gemini API key not found in environment")
        print("   Add GEMINI_API_KEY to your .env file")
    
    # Test service availability
    print("\n🔍 Testing available services:")
    try:
        results = stt.test_services()
        for service, status in results.items():
            if status['available']:
                print(f"✅ {service}: Available")
            else:
                print(f"❌ {service}: {status.get('error', 'Not available')}")
    except Exception as e:
        print(f"❌ Service test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🚀 Setup Instructions:")
    print("1. Get free Gemini API key: https://aistudio.google.com/app/apikey")
    print("2. Add to .env file: GEMINI_API_KEY=your-key-here")
    print("3. Start backend: cd backend && python app.py")
    print("4. Start frontend: cd frontend && npm start")
    print("5. Test in browser: http://localhost:3000")

if __name__ == "__main__":
    test_gemini_integration()
