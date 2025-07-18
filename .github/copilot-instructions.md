# Copilot Instructions

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This is an AI-powered meeting assistant system that consists of:

1. **Recording App**: Records a person answering common meeting questions (video + audio)
2. **Real-time Meeting Integration**: Detects questions during live meetings using speech-to-text and NLP
3. **Response Playback**: Plays pre-recorded or AI-generated responses in real-time

## Architecture Components:
- **Frontend**: React-based recording interface
- **Backend**: Python Flask API for processing
- **AI/ML**: Speech-to-text, NLP question matching, text-to-speech
- **Video Processing**: FFmpeg for video/audio manipulation
- **Real-time**: WebSocket connections for live meeting integration

## Key Technologies:
- Python (Flask, OpenCV, speech_recognition, transformers)
- JavaScript/React for frontend
- WebRTC for real-time video/audio
- Machine Learning for question matching and response generation
