from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Question(db.Model):
    """Model for storing meeting questions."""
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='general')
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    recordings = db.relationship('Recording', backref='question', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Question {self.id}: {self.text[:50]}...>'

class Recording(db.Model):
    """Model for storing video recordings."""
    __tablename__ = 'recordings'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    duration = db.Column(db.Float)  # Duration in seconds
    file_size = db.Column(db.Integer)  # File size in bytes
    thumbnail_path = db.Column(db.String(500))
    transcription = db.Column(db.Text)  # Auto-generated transcription
    status = db.Column(db.String(20), default='active')  # active, archived, deleted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Recording {self.id}: {self.filename}>'

class MeetingSession(db.Model):
    """Model for tracking live meeting sessions."""
    __tablename__ = 'meeting_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True, nullable=False)
    platform = db.Column(db.String(50))  # zoom, teams, meet, etc.
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # active, ended, paused
    
    # Relationships
    interactions = db.relationship('MeetingInteraction', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<MeetingSession {self.session_id}>'

class MeetingInteraction(db.Model):
    """Model for tracking interactions during live meetings."""
    __tablename__ = 'meeting_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('meeting_sessions.id'), nullable=False)
    detected_question = db.Column(db.Text)
    matched_question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    response_type = db.Column(db.String(20))  # recorded, ai_generated
    recording_id = db.Column(db.Integer, db.ForeignKey('recordings.id'))
    ai_response_text = db.Column(db.Text)
    confidence_score = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MeetingInteraction {self.id}: {self.detected_question[:30]}...>'

class UserProfile(db.Model):
    """Model for storing user preferences and profiles."""
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    voice_profile = db.Column(db.String(500))  # Path to voice model
    avatar_settings = db.Column(db.JSON)  # Avatar preferences
    response_tone = db.Column(db.String(50), default='professional')  # professional, casual, friendly
    language = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserProfile {self.name}>'
