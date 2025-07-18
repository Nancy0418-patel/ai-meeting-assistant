#!/usr/bin/env python3
"""
AI Meeting Assistant Setup Checker and Launcher
"""
import os
import sys
from pathlib import Path

def check_environment():
    """Check if environment is properly configured."""
    print("🔍 Checking AI Meeting Assistant Setup...")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  .env file not found!")
            print("📋 Please copy .env.example to .env and add your API keys:")
            print(f"   copy {env_example} {env_file}")
            print()
        else:
            print("❌ No environment configuration found!")
            return False
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("❌ python-dotenv not installed. Run: pip install python-dotenv")
        return False
    
    # Check required dependencies
    print("📦 Checking Dependencies...")
    required_packages = [
        'flask', 'flask_cors', 'flask_sqlalchemy', 'flask_socketio',
        'opencv-python', 'speechrecognition', 'transformers', 
        'requests', 'numpy', 'pillow'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n🚨 Missing packages: {', '.join(missing_packages)}")
        print("📥 Install with: pip install -r backend/requirements.txt")
        return False
    
    # Check API keys
    print("\n🔑 Checking API Keys...")
    api_keys = {
        'OPENAI_API_KEY': 'Required for AI responses and speech-to-text',
        'ELEVENLABS_API_KEY': 'Optional for voice synthesis',
        'GOOGLE_CLOUD_API_KEY': 'Optional for alternative speech-to-text',
        'AZURE_SPEECH_KEY': 'Optional for Azure speech services'
    }
    
    has_required = False
    for key, description in api_keys.items():
        value = os.getenv(key)
        if value:
            print(f"   ✅ {key}: {'*' * 10}{value[-4:] if len(value) > 4 else '****'}")
            if key == 'OPENAI_API_KEY':
                has_required = True
        else:
            status = "❌ Required" if key == 'OPENAI_API_KEY' else "⚠️  Optional"
            print(f"   {status} {key}: {description}")
    
    # Check directories
    print("\n📁 Checking Directories...")
    directories = ['storage', 'storage/recordings', 'storage/audio', 'storage/thumbnails']
    for directory in directories:
        dir_path = Path(directory)
        if dir_path.exists():
            print(f"   ✅ {directory}")
        else:
            print(f"   📁 Creating {directory}")
            dir_path.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 50)
    
    if not has_required:
        print("🚨 SETUP INCOMPLETE")
        print("📝 You need at least an OpenAI API key to get started!")
        print("🔗 Get one here: https://platform.openai.com/api-keys")
        print("💡 Then add it to your .env file: OPENAI_API_KEY=sk-your-key-here")
        return False
    else:
        print("✅ SETUP COMPLETE")
        print("🚀 Ready to launch AI Meeting Assistant!")
        return True

def main():
    """Main launcher function."""
    print("🤖 AI Meeting Assistant Launcher")
    print("=" * 50)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Check setup
    if not check_environment():
        print("\n🛠️  Please complete the setup before launching.")
        print("📖 See API_SETUP.md for detailed instructions.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Ask user what to do
    print("\nWhat would you like to do?")
    print("1. 🚀 Start the application (backend + frontend)")
    print("2. 🔧 Start backend only")
    print("3. 🎨 Start frontend only")
    print("4. 🧪 Test API services")
    print("5. 📖 Open setup guide")
    print("6. ❌ Exit")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == '1':
        start_full_application()
    elif choice == '2':
        start_backend()
    elif choice == '3':
        start_frontend()
    elif choice == '4':
        test_services()
    elif choice == '5':
        open_setup_guide()
    elif choice == '6':
        print("👋 Goodbye!")
        sys.exit(0)
    else:
        print("❌ Invalid choice. Please try again.")
        main()

def start_full_application():
    """Start both backend and frontend."""
    print("\n🚀 Starting AI Meeting Assistant...")
    print("Backend will start on: http://localhost:5000")
    print("Frontend will start on: http://localhost:3000")
    
    import subprocess
    import sys
    
    # Start backend
    backend_process = subprocess.Popen([
        sys.executable, 'backend/app.py'
    ])
    
    # Start frontend (if npm is available)
    try:
        frontend_process = subprocess.Popen([
            'npm', 'start'
        ], cwd='frontend')
        
        print("\n✅ Both services started!")
        print("🌐 Open http://localhost:3000 in your browser")
        input("\nPress Enter to stop all services...")
        
        backend_process.terminate()
        frontend_process.terminate()
        
    except FileNotFoundError:
        print("⚠️  npm not found. Starting backend only.")
        print("🌐 Backend API available at: http://localhost:5000")
        input("\nPress Enter to stop backend...")
        backend_process.terminate()

def start_backend():
    """Start backend only."""
    print("\n🔧 Starting backend server...")
    import subprocess
    import sys
    
    subprocess.run([sys.executable, 'backend/app.py'])

def start_frontend():
    """Start frontend only."""
    print("\n🎨 Starting frontend server...")
    import subprocess
    
    try:
        subprocess.run(['npm', 'start'], cwd='frontend')
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js first.")

def test_services():
    """Test API services."""
    print("\n🧪 Testing API services...")
    
    try:
        import requests
        response = requests.get('http://localhost:5000/api/test-services')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Services test completed!")
            print("🔍 Check the response for detailed results.")
        else:
            print("❌ Backend not running. Start it first with option 2.")
    except Exception as e:
        print(f"❌ Error testing services: {str(e)}")
        print("💡 Make sure the backend is running (option 2)")

def open_setup_guide():
    """Open setup guide."""
    print("\n📖 Opening setup guide...")
    import webbrowser
    import os
    
    guide_path = Path('API_SETUP.md')
    if guide_path.exists():
        # Try to open in default editor
        os.startfile(str(guide_path))
    else:
        print("📄 Setup guide not found. Please check API_SETUP.md")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        input("Press Enter to exit...")
        sys.exit(1)
