# Quick Start Guide - Gemini Speech-to-Text

## Step 1: Get Gemini API Key (FREE)
1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

## Step 2: Setup Environment
1. Create .env file in backend folder:
   ```bash
   cd backend
   cp .env.template .env
   ```

2. Edit .env file and add your Gemini key:
   ```
   GEMINI_API_KEY=your-gemini-api-key-here
   ```

## Step 3: Test the Setup
1. Start backend:
   ```bash
   cd backend
   python app.py
   ```

2. Start frontend:
   ```bash
   cd frontend
   npm start
   ```

3. Go to "Speech Test" tab and click "Test All Services"

## Step 4: Test Speech Recognition
1. Click "Start Recording" to test live audio
2. Or upload an audio file to test file transcription
3. Select "Google Gemini" as the service

## Why Gemini?
- ✅ FREE generous tier
- ✅ High accuracy
- ✅ Supports multiple languages
- ✅ No payment method required to start
- ✅ Easy setup (just need Google account)

Ready to test your speech-to-text system!
