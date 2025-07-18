# Speech-to-Text Service Setup Guide

## Quick Start (Free Options)

### Option 1: Google Gemini (Recommended - Free Tier Available)
- **Cost**: Free tier with generous limits
- **Setup**: Get free API key from Google AI Studio
- **Benefits**: High accuracy, supports audio transcription

### Option 2: OpenAI Whisper (Premium option)
- **Cost**: Very cheap ($0.006 per minute)
- **Setup**: Need OpenAI API key with payment method
- **Benefits**: Highest accuracy, supports many languages

### Option 3: Google Speech Recognition (Basic Free)
- **Cost**: Free (limited usage)
- **Setup**: No API key needed for basic usage
- **Limitations**: Rate limited, requires internet

## API Keys Setup

### 1. Google Gemini (Recommended - Free tier available)
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the API key
5. Add to your .env file:
   ```
   GEMINI_API_KEY=your-gemini-key-here
   ```

### 2. OpenAI Whisper (Premium - $0.006/minute)
1. Go to https://platform.openai.com/
2. Create account and add payment method
3. Go to API Keys section
4. Create new API key
5. Add to your .env file:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```
### 3. Google Cloud Speech-to-Text (Free tier available)
1. Go to https://cloud.google.com/speech-to-text
2. Create Google Cloud account
3. Enable Speech-to-Text API
4. Create service account and download JSON key
5. Add to your .env file:
   ```
   GOOGLE_CLOUD_API_KEY=path/to/your/service-account.json
   ```

### 4. Azure Speech Services (Free tier: 5 hours/month)
1. Go to https://azure.microsoft.com/en-us/services/cognitive-services/speech-to-text/
2. Create Azure account
3. Create Speech resource
4. Get keys and region
5. Add to your .env file:
   ```
   AZURE_SPEECH_KEY=your-key-here
   AZURE_SPEECH_REGION=your-region
   ```

### 5. Deepgram (Free tier: 150 minutes/month)
1. Go to https://deepgram.com/
2. Create account
3. Get API key from dashboard
4. Add to your .env file:
   ```
   DEEPGRAM_API_KEY=your-key-here
   ```

### 6. AssemblyAI (Free tier: 3 hours/month)
1. Go to https://www.assemblyai.com/
2. Create account
3. Get API key from dashboard
4. Add to your .env file:
   ```
   ASSEMBLYAI_API_KEY=your-key-here
   ```

## Testing Order (Recommended)

1. **Start with Google Gemini** (free tier, high accuracy)
2. **Try Free Google Recognition** (built-in, no setup)
3. **Test OpenAI Whisper** (most accurate, very cheap)
4. **Test free tiers** of other services
5. **Use offline recognition** as fallback

## Cost Comparison

| Service | Free Tier | Pay-as-you-go |
|---------|-----------|---------------|
| Google Gemini | Generous free tier | $0.00025/1K chars |
| Google Basic | Limited | N/A |
| OpenAI Whisper | No | $0.006/minute |
| Google Cloud | 60 min/month | $0.006/15 seconds |
| Azure | 5 hours/month | $1/hour |
| Deepgram | 150 min/month | $0.0125/minute |
| AssemblyAI | 3 hours/month | $0.00037/second |

## Quick Setup Instructions

1. Create `.env` file in backend folder
2. Add your API keys (start with Gemini for free tier)
3. Install dependencies: `pip install -r requirements.txt`
4. Test the service with our test endpoint

## Next Steps

1. Set up at least one API key
2. Test the speech-to-text service
3. Integrate with live meeting detection
4. Add real-time transcription
