import os
import cv2
import numpy as np
from PIL import Image
import subprocess
import json
from datetime import timedelta

class VideoProcessor:
    """Service for processing video recordings."""
    
    def __init__(self):
        self.thumbnail_size = (320, 240)
        self.supported_formats = ['.mp4', '.webm', '.avi', '.mov']
    
    def process_video(self, video_path):
        """
        Process uploaded video: extract metadata, create thumbnail, optimize.
        
        Args:
            video_path (str): Path to the video file
            
        Returns:
            dict: Video information including duration, file_size, thumbnail_path
        """
        try:
            # Get video metadata using OpenCV
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise Exception("Could not open video file")
            
            # Extract video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Get file size
            file_size = os.path.getsize(video_path)
            
            # Create thumbnail from middle frame
            thumbnail_path = self._create_thumbnail(cap, video_path, frame_count)
            
            cap.release()
            
            # Optimize video if needed (compress large files)
            if file_size > 50 * 1024 * 1024:  # 50MB threshold
                optimized_path = self._optimize_video(video_path)
                if optimized_path:
                    # Update file path and size after optimization
                    os.replace(optimized_path, video_path)
                    file_size = os.path.getsize(video_path)
            
            return {
                'duration': round(duration, 2),
                'file_size': file_size,
                'thumbnail_path': thumbnail_path,
                'width': width,
                'height': height,
                'fps': fps,
                'frame_count': frame_count
            }
            
        except Exception as e:
            print(f"Error processing video: {str(e)}")
            raise e
    
    def _create_thumbnail(self, cap, video_path, frame_count):
        """Create a thumbnail from the middle frame of the video."""
        try:
            # Seek to middle frame
            middle_frame = frame_count // 2
            cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
            
            ret, frame = cap.read()
            if not ret:
                # Fallback to first frame
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
                
            if not ret:
                raise Exception("Could not extract frame for thumbnail")
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Create PIL Image and resize
            pil_image = Image.fromarray(frame_rgb)
            pil_image.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
            
            # Generate thumbnail path
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            thumbnail_dir = os.path.join(os.path.dirname(video_path), '..', 'thumbnails')
            os.makedirs(thumbnail_dir, exist_ok=True)
            
            thumbnail_path = os.path.join(thumbnail_dir, f"{base_name}_thumb.jpg")
            
            # Save thumbnail
            pil_image.save(thumbnail_path, 'JPEG', quality=85)
            
            return thumbnail_path
            
        except Exception as e:
            print(f"Error creating thumbnail: {str(e)}")
            return None
    
    def _optimize_video(self, video_path):
        """Optimize video file for storage and streaming."""
        try:
            base_name = os.path.splitext(video_path)[0]
            optimized_path = f"{base_name}_optimized.mp4"
            
            # FFmpeg command for optimization
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-c:v', 'libx264',  # H.264 codec
                '-preset', 'medium',  # Encoding speed vs compression
                '-crf', '23',  # Quality (18-28, lower = better quality)
                '-c:a', 'aac',  # Audio codec
                '-b:a', '128k',  # Audio bitrate
                '-movflags', '+faststart',  # Web optimization
                '-y',  # Overwrite output file
                optimized_path
            ]
            
            # Run FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Video optimized: {video_path} -> {optimized_path}")
                return optimized_path
            else:
                print(f"FFmpeg error: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"Error optimizing video: {str(e)}")
            return None
    
    def extract_audio(self, video_path):
        """Extract audio from video file."""
        try:
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            audio_dir = os.path.join(os.path.dirname(video_path), '..', 'audio')
            os.makedirs(audio_dir, exist_ok=True)
            
            audio_path = os.path.join(audio_dir, f"{base_name}.wav")
            
            # FFmpeg command to extract audio
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # WAV format
                '-ar', '16000',  # Sample rate
                '-ac', '1',  # Mono
                '-y',  # Overwrite
                audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return audio_path
            else:
                print(f"Audio extraction error: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"Error extracting audio: {str(e)}")
            return None
    
    def get_video_info(self, video_path):
        """Get detailed video information using ffprobe."""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return None
                
        except Exception as e:
            print(f"Error getting video info: {str(e)}")
            return None
    
    def create_preview_gif(self, video_path, duration=3, fps=10):
        """Create a preview GIF from the video."""
        try:
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            gif_dir = os.path.join(os.path.dirname(video_path), '..', 'previews')
            os.makedirs(gif_dir, exist_ok=True)
            
            gif_path = os.path.join(gif_dir, f"{base_name}_preview.gif")
            
            # FFmpeg command to create GIF
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-t', str(duration),  # Duration
                '-vf', f'fps={fps},scale=320:-1:flags=lanczos',
                '-y',
                gif_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return gif_path
            else:
                print(f"GIF creation error: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"Error creating preview GIF: {str(e)}")
            return None
