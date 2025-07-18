import os
import shutil
import uuid
import time
from werkzeug.utils import secure_filename

class FileManager:
    """Service for managing file uploads and storage."""
    
    def __init__(self, base_upload_path):
        self.base_path = base_upload_path
        self.allowed_video_extensions = {'.mp4', '.webm', '.avi', '.mov', '.mkv'}
        self.allowed_audio_extensions = {'.wav', '.mp3', '.m4a', '.ogg'}
        self.max_file_size = 500 * 1024 * 1024  # 500MB
        
        # Create directory structure
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            'recordings',
            'audio',
            'thumbnails',
            'previews',
            'temp'
        ]
        
        for directory in directories:
            dir_path = os.path.join(self.base_path, directory)
            os.makedirs(dir_path, exist_ok=True)
    
    def save_video(self, file, custom_filename=None):
        """
        Save uploaded video file.
        
        Args:
            file: Flask uploaded file object
            custom_filename: Optional custom filename
            
        Returns:
            str: Path to saved file
        """
        try:
            # Validate file
            if not self._is_valid_video(file):
                raise ValueError("Invalid video file")
            
            # Generate filename
            if custom_filename:
                filename = secure_filename(custom_filename)
            else:
                original_name = secure_filename(file.filename)
                name, ext = os.path.splitext(original_name)
                filename = f"{uuid.uuid4()}{ext}"
            
            # Save to recordings directory
            file_path = os.path.join(self.base_path, 'recordings', filename)
            file.save(file_path)
            
            # Verify file was saved correctly
            if not os.path.exists(file_path):
                raise Exception("File was not saved properly")
            
            return file_path
            
        except Exception as e:
            print(f"Error saving video: {str(e)}")
            raise e
    
    def save_audio(self, file, custom_filename=None):
        """Save uploaded audio file."""
        try:
            if not self._is_valid_audio(file):
                raise ValueError("Invalid audio file")
            
            if custom_filename:
                filename = secure_filename(custom_filename)
            else:
                original_name = secure_filename(file.filename)
                name, ext = os.path.splitext(original_name)
                filename = f"{uuid.uuid4()}{ext}"
            
            file_path = os.path.join(self.base_path, 'audio', filename)
            file.save(file_path)
            
            return file_path
            
        except Exception as e:
            print(f"Error saving audio: {str(e)}")
            raise e
    
    def delete_recording(self, video_path, thumbnail_path=None):
        """Delete a recording and associated files."""
        try:
            # Delete video file
            if os.path.exists(video_path):
                os.remove(video_path)
                print(f"Deleted video: {video_path}")
            
            # Delete thumbnail if provided
            if thumbnail_path and os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
                print(f"Deleted thumbnail: {thumbnail_path}")
            
            # Delete associated audio file if exists
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            audio_path = os.path.join(self.base_path, 'audio', f"{base_name}.wav")
            if os.path.exists(audio_path):
                os.remove(audio_path)
                print(f"Deleted audio: {audio_path}")
            
            # Delete preview GIF if exists
            preview_path = os.path.join(self.base_path, 'previews', f"{base_name}_preview.gif")
            if os.path.exists(preview_path):
                os.remove(preview_path)
                print(f"Deleted preview: {preview_path}")
                
        except Exception as e:
            print(f"Error deleting files: {str(e)}")
            raise e
    
    def get_file_info(self, file_path):
        """Get information about a file."""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            
            return {
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'filename': os.path.basename(file_path),
                'extension': os.path.splitext(file_path)[1].lower()
            }
            
        except Exception as e:
            print(f"Error getting file info: {str(e)}")
            return None
    
    def cleanup_temp_files(self, max_age_hours=24):
        """Clean up temporary files older than specified hours."""
        try:
            temp_dir = os.path.join(self.base_path, 'temp')
            if not os.path.exists(temp_dir):
                return
            
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        print(f"Cleaned up temp file: {filename}")
                        
        except Exception as e:
            print(f"Error cleaning temp files: {str(e)}")
    
    def get_storage_stats(self):
        """Get storage statistics."""
        try:
            stats = {}
            
            for directory in ['recordings', 'audio', 'thumbnails', 'previews']:
                dir_path = os.path.join(self.base_path, directory)
                if os.path.exists(dir_path):
                    total_size = 0
                    file_count = 0
                    
                    for root, dirs, files in os.walk(dir_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            total_size += os.path.getsize(file_path)
                            file_count += 1
                    
                    stats[directory] = {
                        'total_size': total_size,
                        'file_count': file_count,
                        'size_mb': round(total_size / (1024 * 1024), 2)
                    }
            
            return stats
            
        except Exception as e:
            print(f"Error getting storage stats: {str(e)}")
            return {}
    
    def _is_valid_video(self, file):
        """Validate uploaded video file."""
        if not file or not file.filename:
            return False
        
        # Check file extension
        _, ext = os.path.splitext(file.filename.lower())
        if ext not in self.allowed_video_extensions:
            return False
        
        # Check file size (approximate, based on content length)
        if hasattr(file, 'content_length') and file.content_length:
            if file.content_length > self.max_file_size:
                return False
        
        return True
    
    def _is_valid_audio(self, file):
        """Validate uploaded audio file."""
        if not file or not file.filename:
            return False
        
        _, ext = os.path.splitext(file.filename.lower())
        return ext in self.allowed_audio_extensions
    
    def create_backup(self, source_path, backup_name=None):
        """Create a backup of a file."""
        try:
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"Source file not found: {source_path}")
            
            if backup_name:
                backup_filename = backup_name
            else:
                timestamp = str(int(time.time()))
                original_name = os.path.basename(source_path)
                name, ext = os.path.splitext(original_name)
                backup_filename = f"{name}_backup_{timestamp}{ext}"
            
            backup_dir = os.path.join(self.base_path, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            backup_path = os.path.join(backup_dir, backup_filename)
            shutil.copy2(source_path, backup_path)
            
            return backup_path
            
        except Exception as e:
            print(f"Error creating backup: {str(e)}")
            raise e
