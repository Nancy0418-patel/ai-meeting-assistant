# API Keys Setup Guide

## 🚀 Quick Start (Minimal Setup)

For basic functionality, you only need **1 API key**:

### 1. OpenAI API Key (Required)
- **Purpose**: Text generation and speech-to-text
- **Get it**: https://platform.openai.com/api-keys
- **Cost**: ~$0.002 per 1K tokens (very affordable)
- **Used for**: 
  - Generating AI responses when no recording exists
  - Converting audio to text (Whisper)

## 📝 Setup Instructions

### Step 1: Copy Environment File
```bash
# Copy the example file
copy .env.example .env
```

### Step 2: Add Your OpenAI API Key
Edit the `.env` file:
```
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

### Step 3: Test the Setup
1. Run the backend: `python backend/app.py`
2. Visit: http://localhost:5000/api/test-services
3. Check that OpenAI shows as available

## 🎯 Where API Keys Are Used

### Core Features (OpenAI Only)
```
Recording App → Works without any API keys
Question Bank → Works without any API keys
Playback → Works without any API keys
AI Fallback → Requires OPENAI_API_KEY
Speech-to-Text → Requires OPENAI_API_KEY (for live meetings)
```

### Enhanced Features (Optional)
```
Voice Cloning → ELEVENLABS_API_KEY
Alternative STT → GOOGLE_CLOUD_API_KEY, AZURE_SPEECH_KEY
Meeting Integration → ZOOM_CLIENT_ID, TEAMS_CLIENT_ID
```

## 🔧 API Key Configuration by Service

### OpenAI (Required - $5-20/month typical usage)
```env
OPENAI_API_KEY=sk-your-key-here
```
**Used for:**
- ✅ AI response generation
- ✅ Speech-to-text (Whisper)
- ✅ Question context understanding

### ElevenLabs (Optional - Voice Cloning)
```env
ELEVENLABS_API_KEY=your-key-here
```
**Used for:**
- 🎤 Converting AI text responses to natural speech
- 🎤 Voice cloning for realistic audio responses
- **Cost**: ~$5-22/month depending on usage

### Google Cloud (Optional - Alternative STT)
```env
GOOGLE_CLOUD_API_KEY=your-key-here
```
**Used for:**
- 🎤 Alternative speech-to-text service
- 🎤 Better accuracy for certain accents/languages

### Azure Speech (Optional - Alternative STT/TTS)
```env
AZURE_SPEECH_KEY=your-key-here
AZURE_SPEECH_REGION=your-region-here
```
**Used for:**
- 🎤 Alternative speech-to-text service
- 🎤 Text-to-speech alternative to ElevenLabs

## 🏢 Meeting Platform Integration (Optional)

### Zoom Integration
```env
ZOOM_CLIENT_ID=your-zoom-client-id
ZOOM_CLIENT_SECRET=your-zoom-client-secret
```
**Setup**: https://marketplace.zoom.us/

### Microsoft Teams Integration
```env
TEAMS_CLIENT_ID=your-teams-client-id
TEAMS_CLIENT_SECRET=your-teams-client-secret
```
**Setup**: https://portal.azure.com/

### Google Meet Integration
```env
GOOGLE_MEET_CLIENT_ID=your-meet-client-id
GOOGLE_MEET_CLIENT_SECRET=your-meet-client-secret
```
**Setup**: https://console.cloud.google.com/

## 💰 Cost Breakdown

### Minimal Setup (OpenAI only)
- **Monthly cost**: $5-20 for typical usage
- **Per interaction**: ~$0.001-0.01
- **What you get**: Full AI meeting assistant functionality

### Enhanced Setup (All services)
- **Monthly cost**: $20-50 for typical usage
- **Additional features**: Voice cloning, multiple STT options, meeting integrations

## 🛡️ Security Best Practices

### 1. Keep API Keys Secret
- ✅ Never commit `.env` to version control
- ✅ Use different keys for development/production
- ✅ Rotate keys regularly

### 2. Environment Variables
The app loads keys from these locations (in order):
1. `.env` file (recommended)
2. System environment variables
3. Default values (where applicable)

### 3. Test Your Setup
Visit `/api/test-services` to verify all services are working:
```bash
curl http://localhost:5000/api/test-services
```

## 🚨 Troubleshooting

### Common Issues

**"OpenAI API key not found"**
- Check your `.env` file exists
- Verify the key starts with `sk-`
- Restart the backend server

**"Invalid API key"**
- Verify the key is copied correctly
- Check your OpenAI account has credits
- Try regenerating the key

**"Service not available"**
- Some services are optional
- Check the `/api/test-services` endpoint
- Verify your account has access to the specific service

### Testing Individual Services

```bash
# Test OpenAI
curl -X POST http://localhost:5000/api/generate-response \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello, how are you?"}'

# Test all services
curl http://localhost:5000/api/test-services
```

## 🎯 Recommended Setup Flow

1. **Start with OpenAI only** - Get basic functionality working
2. **Add ElevenLabs** - If you want realistic voice responses
3. **Add meeting integrations** - If you need live meeting features
4. **Add alternative STT** - If you need better accuracy or specific language support

## 📞 Support

If you need help with API setup:
1. Check the `/api/test-services` endpoint
2. Verify your `.env` file configuration
3. Check the console logs for detailed error messages
