import os
import requests
import json
from datetime import datetime
import tempfile
import wave
import base64
import io

class SpeechToTextService:
    """Service for converting speech to text using various cloud APIs."""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.azure_key = os.getenv('AZURE_SPEECH_KEY')
        self.azure_region = os.getenv('AZURE_SPEECH_REGION')
        self.deepgram_key = os.getenv('DEEPGRAM_API_KEY')
        self.assemblyai_key = os.getenv('ASSEMBLYAI_API_KEY')
        
        print("SpeechToTextService initialized with cloud APIs only")
    
    def transcribe_audio_file(self, audio_file_path, service='gemini'):
        """
        Transcribe audio file using specified service.
        
        Args:
            audio_file_path (str): Path to audio file
            service (str): Service to use ('openai', 'gemini', 'azure', 'deepgram', 'assemblyai')
            
        Returns:
            dict: Transcription result with text and confidence
        """
        try:
            if service == 'openai' and self.openai_api_key:
                return self._transcribe_with_whisper(audio_file_path)
            elif service == 'gemini' and self.gemini_api_key:
                return self._transcribe_with_gemini(audio_file_path)
            elif service == 'azure' and self.azure_key:
                return self._transcribe_with_azure(audio_file_path)
            elif service == 'deepgram' and self.deepgram_key:
                return self._transcribe_with_deepgram(audio_file_path)
            elif service == 'assemblyai' and self.assemblyai_key:
                return self._transcribe_with_assemblyai(audio_file_path)
            else:
                # Try services in order of preference
                if self.gemini_api_key:
                    return self._transcribe_with_gemini(audio_file_path)
                elif self.openai_api_key:
                    return self._transcribe_with_whisper(audio_file_path)
                elif self.deepgram_key:
                    return self._transcribe_with_deepgram(audio_file_path)
                elif self.azure_key:
                    return self._transcribe_with_azure(audio_file_path)
                elif self.assemblyai_key:
                    return self._transcribe_with_assemblyai(audio_file_path)
                else:
                    return {
                        'text': '',
                        'confidence': 0.0,
                        'error': 'No speech-to-text service available. Please configure API keys.',
                        'service': service
                    }
                
        except Exception as e:
            print(f"Error transcribing audio: {str(e)}")
            return {
                'text': '',
                'confidence': 0.0,
                'error': str(e),
                'service': service
            }
    
    def transcribe_live_audio(self, duration=5, service='openai'):
        """
        Transcribe live audio from microphone.
        
        Args:
            duration (int): Recording duration in seconds
            service (str): Service to use for transcription
            
        Returns:
            dict: Transcription result
        """
        try:
            if not self.microphone:
                return {
                    'text': '',
                    'confidence': 0.0,
                    'error': 'Microphone not available'
                }
            
            print(f"Listening for {duration} seconds...")
            
            with self.microphone as source:
                # Record audio
                audio = self.recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                # Convert to WAV format
                wav_data = audio.get_wav_data()
                tmp_file.write(wav_data)
                tmp_file_path = tmp_file.name
            
            # Transcribe the temporary file
            result = self.transcribe_audio_file(tmp_file_path, service)
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
            return result
            
        except Exception as e:
            print(f"Error transcribing live audio: {str(e)}")
            return {
                'text': '',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _transcribe_with_whisper(self, audio_file_path):
        """Transcribe using OpenAI Whisper."""
        try:
            import openai
            openai.api_key = self.openai_api_key
            
            with open(audio_file_path, 'rb') as audio_file:
                response = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="json"
                )
            
            return {
                'text': response.text,
                'confidence': 1.0,  # Whisper doesn't provide confidence scores
                'service': 'openai_whisper'
            }
            
        except Exception as e:
            print(f"Whisper transcription error: {str(e)}")
            raise e
    
    def _transcribe_with_google(self, audio_file_path):
        """Transcribe using Google Cloud Speech-to-Text."""
        try:
            with sr.AudioFile(audio_file_path) as source:
                audio = self.recognizer.record(source)
            
            result = self.recognizer.recognize_google_cloud(
                audio, 
                credentials_json=self.google_api_key
            )
            
            return {
                'text': result,
                'confidence': 0.8,  # Google doesn't always provide confidence
                'service': 'google_cloud'
            }
            
        except Exception as e:
            print(f"Google Cloud transcription error: {str(e)}")
            raise e
    
    def _transcribe_with_gemini(self, audio_file_path):
        """Transcribe using Google Gemini."""
        try:
            # Convert audio to base64
            with open(audio_file_path, 'rb') as audio_file:
                audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
            
            # Gemini API endpoint
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
            
            headers = {
                'Content-Type': 'application/json',
            }
            
            # Prepare the request payload
            payload = {
                "contents": [{
                    "parts": [
                        {
                            "text": "Please transcribe this audio file. Return only the transcribed text, no additional commentary."
                        },
                        {
                            "inline_data": {
                                "mime_type": "audio/wav",
                                "data": audio_data
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 1000,
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract text from Gemini response
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0].get('content', {})
                    parts = content.get('parts', [])
                    if parts and 'text' in parts[0]:
                        transcribed_text = parts[0]['text'].strip()
                        return {
                            'text': transcribed_text,
                            'confidence': 0.9,  # Gemini doesn't provide confidence scores
                            'service': 'gemini'
                        }
                
                # Fallback if no text found
                return {
                    'text': '',
                    'confidence': 0.0,
                    'error': 'No transcription in Gemini response',
                    'service': 'gemini'
                }
            else:
                error_msg = f"Gemini API error: {response.status_code}"
                if response.text:
                    try:
                        error_detail = response.json()
                        error_msg += f" - {error_detail.get('error', {}).get('message', response.text)}"
                    except:
                        error_msg += f" - {response.text}"
                raise Exception(error_msg)
                
        except Exception as e:
            print(f"Gemini transcription error: {str(e)}")
            raise e
    
    def _transcribe_with_azure(self, audio_file_path):
        """Transcribe using Azure Speech Services."""
        try:
            # Azure Speech SDK would be more comprehensive, but using REST API for simplicity
            url = f"https://{self.azure_region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.azure_key,
                'Content-Type': 'audio/wav; codecs=audio/pcm; samplerate=16000'
            }
            
            with open(audio_file_path, 'rb') as audio_file:
                response = requests.post(url, headers=headers, data=audio_file)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'text': result.get('DisplayText', ''),
                    'confidence': result.get('Confidence', 0.0),
                    'service': 'azure'
                }
            else:
                raise Exception(f"Azure API error: {response.status_code}")
                
        except Exception as e:
            print(f"Azure transcription error: {str(e)}")
            raise e
    
    def _transcribe_with_deepgram(self, audio_file_path):
        """Transcribe using Deepgram."""
        try:
            url = "https://api.deepgram.com/v1/listen"
            
            headers = {
                'Authorization': f'Token {self.deepgram_key}',
                'Content-Type': 'audio/wav'
            }
            
            with open(audio_file_path, 'rb') as audio_file:
                response = requests.post(url, headers=headers, data=audio_file)
            
            if response.status_code == 200:
                result = response.json()
                transcript = result['results']['channels'][0]['alternatives'][0]
                return {
                    'text': transcript['transcript'],
                    'confidence': transcript['confidence'],
                    'service': 'deepgram'
                }
            else:
                raise Exception(f"Deepgram API error: {response.status_code}")
                
        except Exception as e:
            print(f"Deepgram transcription error: {str(e)}")
            raise e
    
    def _transcribe_with_assemblyai(self, audio_file_path):
        """Transcribe using AssemblyAI."""
        try:
            # Upload file first
            upload_url = "https://api.assemblyai.com/v2/upload"
            headers = {"authorization": self.assemblyai_key}
            
            with open(audio_file_path, 'rb') as audio_file:
                response = requests.post(upload_url, headers=headers, data=audio_file)
            
            audio_url = response.json()['upload_url']
            
            # Request transcription
            transcript_url = "https://api.assemblyai.com/v2/transcript"
            data = {"audio_url": audio_url}
            
            response = requests.post(transcript_url, json=data, headers=headers)
            transcript_id = response.json()['id']
            
            # Poll for completion
            polling_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
            
            while True:
                response = requests.get(polling_url, headers=headers)
                result = response.json()
                
                if result['status'] == 'completed':
                    return {
                        'text': result['text'],
                        'confidence': result['confidence'],
                        'service': 'assemblyai'
                    }
                elif result['status'] == 'error':
                    raise Exception(f"AssemblyAI error: {result['error']}")
                
                # Wait before polling again
                import time
                time.sleep(2)
                
        except Exception as e:
            print(f"AssemblyAI transcription error: {str(e)}")
            raise e
    
    def _transcribe_offline(self, audio_file_path):
        """Transcribe using offline speech recognition."""
        try:
            with sr.AudioFile(audio_file_path) as source:
                audio = self.recognizer.record(source)
            
            # Try different offline methods
            try:
                result = self.recognizer.recognize_sphinx(audio)
                return {
                    'text': result,
                    'confidence': 0.6,
                    'service': 'offline_sphinx'
                }
            except:
                # Fallback to basic recognition
                result = self.recognizer.recognize_google(audio)  # This actually uses Google's free service
                return {
                    'text': result,
                    'confidence': 0.7,
                    'service': 'offline_google'
                }
                
        except Exception as e:
            print(f"Offline transcription error: {str(e)}")
            return {
                'text': '',
                'confidence': 0.0,
                'error': str(e),
                'service': 'offline'
            }
    
    def test_services(self):
        """Test all available STT services."""
        results = {}
        
        # Create a test audio file (1 second of silence)
        test_audio_path = tempfile.mktemp(suffix='.wav')
        
        try:
            # Create a simple test audio file
            with wave.open(test_audio_path, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(16000)
                wav_file.writeframes(b'\x00' * 32000)  # 1 second of silence
            
            # Test each service
            services = ['openai', 'gemini', 'google', 'azure', 'deepgram', 'assemblyai']
            
            for service in services:
                try:
                    result = self.transcribe_audio_file(test_audio_path, service)
                    results[service] = {
                        'available': True,
                        'test_result': result
                    }
                except Exception as e:
                    results[service] = {
                        'available': False,
                        'error': str(e)
                    }
            
        finally:
            # Clean up test file
            if os.path.exists(test_audio_path):
                os.unlink(test_audio_path)
        
        return results
