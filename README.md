# AI Meeting Assistant

An AI-powered meeting assistant system that records a person answering common meeting questions and plays pre-recorded or AI-generated responses during live meetings.

## Project Structure

```
ai-meeting-assistant/
├── backend/                    # Python Flask API
│   ├── app.py                 # Main Flask application
│   ├── models/                # Database models
│   ├── services/              # Business logic
│   ├── utils/                 # Utility functions
│   └── requirements.txt       # Python dependencies
├── frontend/                  # React recording interface
│   ├── src/                   # React source code
│   ├── public/                # Static files
│   └── package.json          # Node.js dependencies
├── ai_services/              # AI/ML processing
│   ├── speech_to_text.py     # STT processing
│   ├── question_matcher.py   # NLP question matching
│   ├── response_generator.py # AI response generation
│   └── video_processor.py    # Video processing
├── storage/                  # File storage
│   ├── recordings/           # Video recordings
│   ├── audio/               # Audio files
│   └── database/            # SQLite database
└── docs/                    # Documentation
    └── ARCHITECTURE.md      # System architecture
```

## Features

### Phase 1: Recording System ✅ (Current)
- Web-based video recording interface
- Pre-defined question bank
- Video and audio processing
- Question tagging and storage

### Phase 2: Live Meeting Integration
- Real-time audio capture
- Speech-to-text processing
- Question detection and matching
- Response playback system

### Phase 3: AI Enhancement
- AI-generated responses for unknown questions
- Voice cloning and synthesis
- Avatar animation
- Learning from interactions

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   cd frontend && npm install
   ```

2. **Run Backend**:
   ```bash
   cd backend && python app.py
   ```

3. **Run Frontend**:
   ```bash
   cd frontend && npm start
   ```

4. **Access Application**:
   - Recording Interface: http://localhost:3000
   - API Documentation: http://localhost:5000/docs

## Technology Stack

- **Backend**: Python, Flask, OpenCV, FFmpeg
- **Frontend**: React, WebRTC, MediaRecorder API
- **AI/ML**: OpenAI GPT-4, Whisper, Transformers
- **Database**: SQLite (development), PostgreSQL (production)
- **Real-time**: WebSocket, Socket.io

## License

MIT License
