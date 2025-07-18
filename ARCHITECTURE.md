# AI Meeting Assistant System Architecture

## System Overview
```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AI MEETING ASSISTANT SYSTEM                      │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   RECORDING      │    │   LIVE MEETING   │    │   AI RESPONSE    │
│     PHASE        │    │     PHASE        │    │   GENERATION     │
└──────────────────┘    └──────────────────┘    └──────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Video Recorder  │    │ Audio Capture    │    │ GPT-4 + TTS      │
│  Question Bank   │    │ Speech-to-Text   │    │ Avatar Generator │
│  Storage System  │    │ Question Matcher │    │ Voice Cloning    │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

## Detailed Architecture

### 1. Pre-Recording System
```
┌─────────────────────────────────────────────────────────────────┐
│                      RECORDING SYSTEM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Web UI     │  │ Video       │  │  Question Database      │  │
│  │  Recording  │◄─┤ Processing  │◄─┤  - Common Questions     │  │
│  │  Interface  │  │ (FFmpeg)    │  │  - Custom Questions     │  │
│  └─────────────┘  └─────────────┘  │  - Tags & Categories    │  │
│         │                          └─────────────────────────┘  │
│         ▼                                      │                │
│  ┌─────────────────────────────────────────────┼────────────┐   │
│  │           File Storage System               │            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────▼──────────┐  │   │
│  │  │ Video Files │  │ Audio Files │  │ Question Index  │  │   │
│  │  │ (.mp4)      │  │ (.wav)      │  │ (embeddings)    │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Live Meeting Integration
```
┌─────────────────────────────────────────────────────────────────┐
│                   LIVE MEETING SYSTEM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Meeting     │  │ Real-time   │  │  Question Detection     │  │
│  │ Audio       │─►│ Speech-to   │─►│  - NLP Processing       │  │
│  │ Capture     │  │ Text (STT)  │  │  - Similarity Search    │  │
│  └─────────────┘  └─────────────┘  │  - Context Awareness    │  │
│         ▲                          └─────────────────────────┘  │
│         │                                      │                │
│  ┌──────┴──────┐                              ▼                │
│  │ Meeting     │                    ┌─────────────────────────┐  │
│  │ Platforms   │                    │  Response Selector      │  │
│  │ - Zoom      │                    │  - Pre-recorded Match   │  │
│  │ - Teams     │                    │  - AI Generation        │  │
│  │ - Google    │                    │  - Confidence Scoring   │  │
│  │   Meet      │                    └─────────────────────────┘  │
│  └─────────────┘                                │                │
│                                                 ▼                │
│                                   ┌─────────────────────────┐    │
│                                   │  Response Delivery      │    │
│                                   │  - Video Injection      │    │
│                                   │  - Audio Playback       │    │
│                                   │  - Virtual Camera       │    │
│                                   └─────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 3. AI Response Generation
```
┌─────────────────────────────────────────────────────────────────┐
│                 AI RESPONSE GENERATION                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Question    │  │ AI Models   │  │  Response Creation      │  │
│  │ Context +   │─►│ - GPT-4     │─►│  - Text Generation      │  │
│  │ History     │  │ - Claude    │  │  - Voice Synthesis      │  │
│  └─────────────┘  │ - Local LLM │  │  - Avatar Animation     │  │
│         ▲          └─────────────┘  └─────────────────────────┘  │
│         │                                      │                │
│  ┌──────┴──────┐                              ▼                │
│  │ User        │                    ┌─────────────────────────┐  │
│  │ Profile &   │                    │  Media Pipeline         │  │
│  │ Preferences │                    │  - Video Composition    │  │
│  │ - Tone      │                    │  - Audio Mixing         │  │
│  │ - Style     │                    │  - Real-time Streaming  │  │
│  │ - Language  │                    └─────────────────────────┘  │
│  └─────────────┘                                │                │
│                                                 ▼                │
│                                   ┌─────────────────────────┐    │
│                                   │  Quality Assurance      │    │
│                                   │  - Response Validation  │    │
│                                   │  - A/B Testing          │    │
│                                   │  - Feedback Learning    │    │
│                                   └─────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend (Python)
- **Flask/FastAPI**: Main API server
- **OpenCV**: Video processing
- **speech_recognition**: Audio processing
- **transformers**: NLP and embeddings
- **SQLite/PostgreSQL**: Database
- **Redis**: Caching and real-time data

### Frontend (React)
- **React**: User interface
- **WebRTC**: Real-time video/audio
- **Socket.io**: Real-time communication
- **MediaRecorder API**: Browser recording

### AI/ML Services
- **OpenAI GPT-4**: Text generation
- **ElevenLabs**: Voice synthesis
- **Whisper**: Speech-to-text
- **sentence-transformers**: Question matching

### Infrastructure
- **FFmpeg**: Video/audio processing
- **OBS**: Virtual camera output
- **Docker**: Containerization
- **WebSocket**: Real-time communication

## Data Flow

1. **Recording Phase**:
   ```
   User Records → Video Processing → Question Tagging → Storage → Embedding Generation
   ```

2. **Live Meeting Phase**:
   ```
   Audio Capture → STT → Question Detection → Response Selection → Media Playback
   ```

3. **AI Generation Phase**:
   ```
   Question Context → LLM Processing → TTS Generation → Avatar Creation → Stream Output
   ```

## Key Features

### Recording App
- ✅ Web-based recording interface
- ✅ Pre-defined question bank
- ✅ Custom question creation
- ✅ Video quality optimization
- ✅ Automatic transcription
- ✅ Question tagging system

### Live Meeting Integration
- ✅ Real-time audio monitoring
- ✅ Question detection algorithms
- ✅ Context-aware responses
- ✅ Multiple meeting platform support
- ✅ Virtual camera integration

### AI Response System
- ✅ Fallback AI generation
- ✅ Voice cloning
- ✅ Avatar animation
- ✅ Personalized responses
- ✅ Learning from interactions

## Security & Privacy
- End-to-end encryption for recordings
- Local processing options
- GDPR compliance
- User consent management
- Secure API authentication
