#!/usr/bin/env python3
"""
Test script for SSL certificate issues with HuggingFace models.
This script helps diagnose and fix SSL certificate problems.
"""

import os
import sys
import ssl
import urllib.request
import urllib.error
from pathlib import Path

def test_ssl_connection():
    """Test SSL connection to HuggingFace."""
    print("Testing SSL connection to HuggingFace...")
    
    try:
        # Test connection to HuggingFace
        url = "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2"
        response = urllib.request.urlopen(url, timeout=10)
        print("✓ SSL connection to HuggingFace successful")
        return True
    except urllib.error.URLError as e:
        print(f"✗ SSL connection failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False

def test_sentence_transformers():
    """Test sentence-transformers import and model loading."""
    print("\nTesting sentence-transformers...")
    
    try:
        import sentence_transformers
        print(f"✓ sentence-transformers version: {sentence_transformers.__version__}")
        
        # Try to load a model
        from sentence_transformers import SentenceTransformer
        
        print("Attempting to load model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓ Model loaded successfully")
        
        # Test encoding
        test_text = "This is a test sentence"
        embedding = model.encode([test_text])
        print(f"✓ Encoding successful, shape: {embedding.shape}")
        
        return True
        
    except ImportError:
        print("✗ sentence-transformers not installed")
        return False
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return False

def fix_ssl_certificates():
    """Try to fix SSL certificate issues."""
    print("\nAttempting SSL certificate fixes...")
    
    try:
        # Method 1: Update certificates
        print("1. Updating certificates...")
        import ssl
        import certifi
        
        # Set certificate bundle
        os.environ['SSL_CERT_FILE'] = certifi.where()
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        print(f"✓ Certificate bundle set to: {certifi.where()}")
        
        # Method 2: Disable SSL verification (NOT RECOMMENDED for production)
        print("2. Disabling SSL verification...")
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Set environment variables
        os.environ['CURL_CA_BUNDLE'] = ''
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        
        print("✓ SSL verification disabled")
        
        # Method 3: Try with urllib3
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            print("✓ urllib3 warnings disabled")
        except ImportError:
            print("⚠ urllib3 not available")
        
        return True
        
    except Exception as e:
        print(f"✗ Error fixing SSL: {e}")
        return False

def create_offline_setup():
    """Create instructions for offline/airgapped setup."""
    print("\nCreating offline setup instructions...")
    
    instructions = """
# Offline Setup Instructions

If you're in an airgapped environment or have persistent SSL issues, follow these steps:

## Option 1: Download models manually
1. Go to https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
2. Download all files in the repository
3. Place them in: ~/.cache/huggingface/transformers/models--sentence-transformers--all-MiniLM-L6-v2/
4. Set environment variable: TRANSFORMERS_OFFLINE=1

## Option 2: Use simple text matching
1. The application will automatically fall back to simple text matching
2. This doesn't require any model downloads
3. Performance will be lower but it will work without internet

## Option 3: Use local models
1. Download pre-trained models on another machine
2. Copy the entire ~/.cache/huggingface/ directory
3. Set TRANSFORMERS_OFFLINE=1

## Option 4: Corporate network setup
1. Contact your IT team about SSL certificate issues
2. They may need to install corporate certificates
3. Or configure proxy settings for pip and Python
"""
    
    with open("OFFLINE_SETUP.md", "w") as f:
        f.write(instructions)
    
    print("✓ Created OFFLINE_SETUP.md with detailed instructions")

def main():
    """Main test function."""
    print("SSL Certificate and Model Loading Test")
    print("=" * 50)
    
    # Test SSL connection
    ssl_ok = test_ssl_connection()
    
    # Test sentence transformers
    if ssl_ok:
        model_ok = test_sentence_transformers()
        if model_ok:
            print("\n✓ All tests passed! Your setup should work.")
            return
    
    # Try to fix SSL issues
    print("\n" + "=" * 50)
    print("Attempting to fix SSL issues...")
    fix_ssl_certificates()
    
    # Test again
    print("\n" + "=" * 50)
    print("Testing again after fixes...")
    if test_sentence_transformers():
        print("\n✓ Fixed! Your setup should now work.")
    else:
        print("\n⚠ Still having issues. Creating offline setup instructions...")
        create_offline_setup()
        print("\nThe application will use simple text matching as fallback.")

if __name__ == "__main__":
    main()
