from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
import os
import json
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from dotenv import load_dotenv
from services.video_processor import VideoProcessor
from services.question_matcher import QuestionMatcher
from services.ai_response_generator import AIResponseGenerator
from services.speech_to_text import SpeechToTextService
from models.database import db, Recording, Question
from utils.file_manager import FileManager

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meeting_assistant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'storage')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# API Keys from environment variables
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
app.config['ELEVENLABS_API_KEY'] = os.getenv('ELEVENLABS_API_KEY')
app.config['GOOGLE_CLOUD_API_KEY'] = os.getenv('GOOGLE_CLOUD_API_KEY')
app.config['AZURE_SPEECH_KEY'] = os.getenv('AZURE_SPEECH_KEY')
app.config['AZURE_SPEECH_REGION'] = os.getenv('AZURE_SPEECH_REGION')

# Initialize extensions
CORS(app, origins=["http://localhost:3000"])
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize services
video_processor = VideoProcessor()
question_matcher = QuestionMatcher()
file_manager = FileManager(app.config['UPLOAD_FOLDER'])
ai_generator = AIResponseGenerator()
stt_service = SpeechToTextService()

# Ensure upload directories exist
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'recordings'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'audio'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails'), exist_ok=True)

@app.before_request
def create_tables():
    """Create database tables and populate with default questions."""
    if not hasattr(create_tables, 'called'):
        create_tables.called = True
        db.create_all()
        
        # Add default questions if none exist
        if Question.query.count() == 0:
            default_questions = [
                "Can you introduce yourself?",
                "What's your role in this project?",
                "What are your thoughts on this proposal?",
                "Do you have any questions or concerns?",
                "What's your availability for the next phase?",
                "Can you provide a status update?",
                "What are the next steps?",
                "Do you agree with this approach?",
                "What's your opinion on the timeline?",
                "Any blockers or dependencies?",
                "What resources do you need?",
                "Can you walk us through your findings?",
                "What are the risks involved?",
                "How do you see this impacting the project?",
                "What's your recommendation?"
                ]
            
            for q_text in default_questions:
                question = Question(
                    text=q_text,
                    category="general",
                    is_default=True
                )
                db.session.add(question)
            
            db.session.commit()
            print("Default questions added to database")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/questions', methods=['GET'])
def get_questions():
    """Get all available questions."""
    questions = Question.query.all()
    return jsonify([{
        'id': q.id,
        'text': q.text,
        'category': q.category,
        'is_default': q.is_default,
        'created_at': q.created_at.isoformat()
    } for q in questions])

@app.route('/api/questions', methods=['POST'])
def add_question():
    """Add a new custom question."""
    data = request.json
    
    if not data or 'text' not in data:
        return jsonify({'error': 'Question text is required'}), 400
    
    question = Question(
        text=data['text'],
        category=data.get('category', 'custom'),
        is_default=False
    )
    
    db.session.add(question)
    db.session.commit()
    
    return jsonify({
        'id': question.id,
        'text': question.text,
        'category': question.category,
        'message': 'Question added successfully'
    }), 201

@app.route('/api/recordings', methods=['GET'])
def get_recordings():
    """Get all recordings."""
    recordings = Recording.query.order_by(Recording.created_at.desc()).all()
    return jsonify([{
        'id': r.id,
        'question_id': r.question_id,
        'question_text': r.question.text if r.question else 'Unknown',
        'filename': r.filename,
        'duration': r.duration,
        'file_size': r.file_size,
        'thumbnail_path': r.thumbnail_path,
        'created_at': r.created_at.isoformat()
    } for r in recordings])

@app.route('/api/upload', methods=['POST'])
def upload_recording():
    """Upload and process a video recording."""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        question_id = request.form.get('question_id')
        
        if not question_id:
            return jsonify({'error': 'Question ID is required'}), 400
        
        if video_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate question exists
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'error': 'Invalid question ID'}), 400
        
        # Generate unique filename
        file_extension = os.path.splitext(video_file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Save video file
        video_path = file_manager.save_video(video_file, unique_filename)
        
        # Process video (extract duration, create thumbnail, etc.)
        video_info = video_processor.process_video(video_path)
        
        # Create database record
        recording = Recording(
            question_id=question_id,
            filename=unique_filename,
            file_path=video_path,
            duration=video_info['duration'],
            file_size=video_info['file_size'],
            thumbnail_path=video_info['thumbnail_path']
        )
        
        db.session.add(recording)
        db.session.commit()
        
        return jsonify({
            'id': recording.id,
            'message': 'Recording uploaded and processed successfully',
            'filename': unique_filename,
            'duration': video_info['duration'],
            'thumbnail_path': video_info['thumbnail_path']
        }), 201
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': 'Failed to process upload'}), 500

@app.route('/api/recordings/<int:recording_id>/play', methods=['GET'])
def play_recording(recording_id):
    """Stream a recording for playback."""
    recording = Recording.query.get_or_404(recording_id)
    
    try:
        return send_from_directory(
            os.path.dirname(recording.file_path),
            os.path.basename(recording.file_path),
            as_attachment=False
        )
    except Exception as e:
        return jsonify({'error': 'File not found'}), 404

@app.route('/api/recordings/<int:recording_id>', methods=['DELETE'])
def delete_recording(recording_id):
    """Delete a recording."""
    recording = Recording.query.get_or_404(recording_id)
    
    try:
        # Delete files
        file_manager.delete_recording(recording.file_path, recording.thumbnail_path)
        
        # Delete database record
        db.session.delete(recording)
        db.session.commit()
        
        return jsonify({'message': 'Recording deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': 'Failed to delete recording'}), 500

# WebSocket events for real-time features
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    emit('status', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')

@socketio.on('recording_started')
def handle_recording_started(data):
    """Handle recording start event."""
    print(f"Recording started for question: {data.get('question_id')}")
    emit('recording_status', {'status': 'recording', 'question_id': data.get('question_id')})

@socketio.on('recording_stopped')
def handle_recording_stopped(data):
    """Handle recording stop event."""
    print(f"Recording stopped for question: {data.get('question_id')}")
    emit('recording_status', {'status': 'stopped', 'question_id': data.get('question_id')})

@app.route('/api/test-services', methods=['GET'])
def test_ai_services():
    """Test all AI services and show configuration status."""
    try:
        # Test AI services
        ai_results = ai_generator.test_services()
        stt_results = stt_service.test_services()
        
        # Check environment variables
        env_status = {
            'OPENAI_API_KEY': bool(os.getenv('OPENAI_API_KEY')),
            'ELEVENLABS_API_KEY': bool(os.getenv('ELEVENLABS_API_KEY')),
            'GOOGLE_CLOUD_API_KEY': bool(os.getenv('GOOGLE_CLOUD_API_KEY')),
            'AZURE_SPEECH_KEY': bool(os.getenv('AZURE_SPEECH_KEY')),
            'DEEPGRAM_API_KEY': bool(os.getenv('DEEPGRAM_API_KEY')),
            'ASSEMBLYAI_API_KEY': bool(os.getenv('ASSEMBLYAI_API_KEY')),
        }
        
        return jsonify({
            'ai_services': ai_results,
            'stt_services': stt_results,
            'environment_variables': env_status,
            'setup_instructions': {
                'message': 'Copy .env.example to .env and add your API keys',
                'required_for_basic_functionality': ['OPENAI_API_KEY'],
                'optional_for_enhanced_features': ['ELEVENLABS_API_KEY', 'GOOGLE_CLOUD_API_KEY', 'AZURE_SPEECH_KEY']
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Error testing AI services'
        }), 500

@app.route('/api/generate-response', methods=['POST'])
def generate_ai_response():
    """Generate AI response for a question."""
    try:
        data = request.json
        question = data.get('question')
        context = data.get('context', '')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        # Generate response
        response = ai_generator.generate_complete_response(question, context)
        
        return jsonify({
            'response': response,
            'message': 'Response generated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Error generating AI response'
        }), 500
    
@app.route('/api/speech-to-text/test', methods=['GET'])
def test_speech_services():
    """Test all available speech-to-text services."""
    try:
        results = stt_service.test_services()
        return jsonify({
            'status': 'success',
            'services': results,
            'message': 'Speech-to-text services tested'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/speech-to-text/transcribe', methods=['POST'])
def transcribe_audio():
    """Transcribe uploaded audio file."""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        service = request.form.get('service', 'openai')
        
        if audio_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save temporary file
        temp_path = file_manager.save_audio(audio_file)
        
        # Transcribe
        result = stt_service.transcribe_audio_file(temp_path, service)
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify({
            'status': 'success',
            'transcription': result,
            'service_used': service
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/speech-to-text/live', methods=['POST'])
def live_transcription():
    """Start live transcription from microphone."""
    try:
        data = request.json or {}
        duration = data.get('duration', 5)
        service = data.get('service', 'openai')
        
        result = stt_service.transcribe_live_audio(duration, service)
        
        return jsonify({
            'status': 'success',
            'transcription': result,
            'service_used': service
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
    

if __name__ == '__main__':
    with app.app_context():
        create_tables()
    
    print("Starting AI Meeting Assistant Backend...")
    print("Access the API at: http://localhost:5000")
    print("WebSocket endpoint: ws://localhost:5000")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
