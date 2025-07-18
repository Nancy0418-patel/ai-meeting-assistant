import os
import openai
import requests
import json
from datetime import datetime
from flask import current_app

class AIResponseGenerator:
    """Service for generating AI responses when no pre-recorded answer exists."""
    
    def __init__(self):
        self.openai_client = None
        self.elevenlabs_api_key = None
        self.initialize_services()
    
    def initialize_services(self):
        """Initialize AI services with API keys."""
        try:
            # Initialize OpenAI
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                openai.api_key = openai_key
                self.openai_client = openai
                print("OpenAI service initialized")
            else:
                print("Warning: OpenAI API key not found")
            
            # Initialize ElevenLabs
            self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
            if self.elevenlabs_api_key:
                print("ElevenLabs service initialized")
            else:
                print("Warning: ElevenLabs API key not found")
                
        except Exception as e:
            print(f"Error initializing AI services: {str(e)}")
    
    def generate_text_response(self, question, context=None, user_profile=None):
        """
        Generate a text response using OpenAI GPT-4.
        
        Args:
            question (str): The question to answer
            context (str): Optional context from the meeting
            user_profile (dict): Optional user profile for personalization
            
        Returns:
            str: Generated response text
        """
        try:
            if not self.openai_client:
                return "AI service not available. Please configure OpenAI API key."
            
            # Build the prompt
            system_prompt = self._build_system_prompt(user_profile)
            user_prompt = self._build_user_prompt(question, context)
            
            # Generate response using OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating text response: {str(e)}")
            return f"I apologize, but I'm unable to provide a response at the moment. Regarding '{question}', I'll need to get back to you on that."
    
    def generate_voice_response(self, text, voice_id=None):
        """
        Generate voice audio from text using ElevenLabs.
        
        Args:
            text (str): Text to convert to speech
            voice_id (str): Optional specific voice ID
            
        Returns:
            bytes: Audio data
        """
        try:
            if not self.elevenlabs_api_key:
                print("ElevenLabs API key not configured")
                return None
            
            # Default voice ID (you can customize this)
            if not voice_id:
                voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error generating voice response: {str(e)}")
            return None
    
    def generate_complete_response(self, question, context=None, user_profile=None):
        """
        Generate both text and voice response.
        
        Args:
            question (str): The question to answer
            context (str): Optional context
            user_profile (dict): Optional user profile
            
        Returns:
            dict: Contains 'text' and 'audio' (if available)
        """
        try:
            # Generate text response
            text_response = self.generate_text_response(question, context, user_profile)
            
            # Generate voice response
            audio_response = self.generate_voice_response(text_response)
            
            return {
                'text': text_response,
                'audio': audio_response,
                'timestamp': datetime.utcnow().isoformat(),
                'question': question
            }
            
        except Exception as e:
            print(f"Error generating complete response: {str(e)}")
            return {
                'text': f"I apologize, but I'm unable to provide a response at the moment.",
                'audio': None,
                'timestamp': datetime.utcnow().isoformat(),
                'question': question
            }
    
    def _build_system_prompt(self, user_profile=None):
        """Build system prompt for AI responses."""
        base_prompt = """You are an AI assistant representing a professional in a business meeting. 
        Your responses should be:
        - Professional and concise
        - Appropriate for a business context
        - Between 1-3 sentences
        - Natural sounding when spoken aloud
        - Helpful and informative
        
        You are responding as if you are the person who would normally be in this meeting."""
        
        if user_profile:
            name = user_profile.get('name', 'the team member')
            role = user_profile.get('role', 'team member')
            tone = user_profile.get('response_tone', 'professional')
            
            base_prompt += f"\n\nYou are representing {name}, who is a {role}. "
            base_prompt += f"Your response tone should be {tone}."
        
        return base_prompt
    
    def _build_user_prompt(self, question, context=None):
        """Build user prompt with question and context."""
        prompt = f"Please respond to this meeting question: {question}"
        
        if context:
            prompt += f"\n\nMeeting context: {context}"
        
        return prompt
    
    def test_services(self):
        """Test all AI services to verify they're working."""
        results = {
            'openai': False,
            'elevenlabs': False,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Test OpenAI
        try:
            if self.openai_client:
                test_response = self.generate_text_response("Hello, this is a test.")
                if test_response and len(test_response) > 0:
                    results['openai'] = True
                    results['openai_response'] = test_response[:100] + "..."
        except Exception as e:
            results['openai_error'] = str(e)
        
        # Test ElevenLabs
        try:
            if self.elevenlabs_api_key:
                test_audio = self.generate_voice_response("Hello, this is a test.")
                if test_audio:
                    results['elevenlabs'] = True
                    results['elevenlabs_audio_size'] = len(test_audio)
        except Exception as e:
            results['elevenlabs_error'] = str(e)
        
        return results
