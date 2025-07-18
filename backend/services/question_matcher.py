import numpy as np
import pickle
import os
import re
import string
import ssl
import warnings
from sklearn.metrics.pairwise import cosine_similarity

# Handle SSL certificate issues
try:
    # Try to create an unverified context if we have SSL issues
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
except:
    ssl_context = None

class QuestionMatcher:
    """Service for matching detected questions to recorded responses."""
    
    def __init__(self):
        # Initialize sentence transformer model for embeddings
        self.model = None
        self.use_simple_matching = False
        self.question_embeddings = {}
        self.questions_cache = {}
        self.similarity_threshold = 0.7  # Minimum similarity for a match
        
        # Try to initialize the sentence transformer model
        self._initialize_model()
        
        # Common question patterns for better matching
        self.question_patterns = [
            r"^(what|how|when|where|why|who|which|can|could|would|will|do|does|did|is|are|was|were)",
            r"\?$",  # Ends with question mark
            r"(please|could you|can you|would you)",
        ]
    
    def _initialize_model(self):
        """Initialize the sentence transformer model with SSL error handling."""
        try:
            # Try to import and initialize sentence transformers
            from sentence_transformers import SentenceTransformer
            
            print("Attempting to load sentence transformer model...")
            
            # Try different approaches to handle SSL issues
            try:
                # First try: normal initialization
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✓ Successfully loaded sentence transformer model")
                
            except Exception as e:
                if "SSL" in str(e) or "certificate" in str(e).lower():
                    print(f"SSL Error detected: {str(e)}")
                    print("Attempting to load model with SSL verification disabled...")
                    
                    # Try with SSL verification disabled
                    import os
                    os.environ['CURL_CA_BUNDLE'] = ''
                    os.environ['REQUESTS_CA_BUNDLE'] = ''
                    
                    # Disable SSL warnings
                    import urllib3
                    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    
                    try:
                        self.model = SentenceTransformer('all-MiniLM-L6-v2', 
                                                       trust_remote_code=True)
                        print("✓ Successfully loaded model with SSL verification disabled")
                    except Exception as e2:
                        print(f"Still failed to load model: {str(e2)}")
                        raise e2
                else:
                    raise e
                    
        except ImportError:
            print("⚠ sentence-transformers not available, using simple text matching")
            self.use_simple_matching = True
            self.model = None
            
        except Exception as e:
            print(f"⚠ Failed to load sentence transformer model: {str(e)}")
            print("Falling back to simple text matching")
            self.use_simple_matching = True
            self.model = None
    
    def load_questions(self, questions_data):
        """
        Load questions and create embeddings for matching.
        
        Args:
            questions_data: List of dicts with 'id', 'text', and other fields
        """
        try:
            self.questions_cache = {q['id']: q for q in questions_data}
            
            if not self.use_simple_matching and self.model:
                # Create embeddings for all questions using sentence transformer
                question_texts = [q['text'] for q in questions_data]
                embeddings = self.model.encode(question_texts)
                
                # Store embeddings with question IDs
                for i, question in enumerate(questions_data):
                    self.question_embeddings[question['id']] = embeddings[i]
                
                print(f"Loaded {len(questions_data)} questions with ML embeddings")
            else:
                # Simple text matching fallback
                print(f"Loaded {len(questions_data)} questions with simple text matching")
            
        except Exception as e:
            print(f"Error loading questions: {str(e)}")
            print("Falling back to simple text matching")
            self.use_simple_matching = True
            self.model = None
    
    def find_best_match(self, detected_text, context=None):
        """
        Find the best matching question for detected text.
        
        Args:
            detected_text (str): Text detected from speech
            context (str): Optional context from conversation
            
        Returns:
            dict: Match result with question_id, confidence, and matched_text
        """
        try:
            if not detected_text or not self.questions_cache:
                return None
            
            # Preprocess the detected text
            processed_text = self._preprocess_text(detected_text)
            
            # Check if text looks like a question
            if not self._is_likely_question(processed_text):
                return None
            
            if not self.use_simple_matching and self.model and self.question_embeddings:
                # Use ML-based matching
                return self._find_match_ml(processed_text, detected_text)
            else:
                # Use simple text matching
                return self._find_match_simple(processed_text, detected_text)
                
        except Exception as e:
            print(f"Error finding match: {str(e)}")
            return None
    
    def _find_match_ml(self, processed_text, detected_text):
        """Find match using ML embeddings."""
        try:
            # Create embedding for detected text
            detected_embedding = self.model.encode([processed_text])[0]
            
            # Calculate similarities with all stored questions
            best_match = None
            highest_similarity = 0
            
            for question_id, question_embedding in self.question_embeddings.items():
                similarity = cosine_similarity([detected_embedding], [question_embedding])[0][0]
                
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_match = {
                        'question_id': question_id,
                        'confidence': similarity,
                        'matched_text': self.questions_cache[question_id]['text'],
                        'detected_text': detected_text,
                        'method': 'ml'
                    }
            
            # Return match only if confidence is above threshold
            if best_match and best_match['confidence'] >= self.similarity_threshold:
                return best_match
            
            return None
            
        except Exception as e:
            print(f"Error in ML matching: {str(e)}")
            return None
    
    def _find_match_simple(self, processed_text, detected_text):
        """Find match using simple text similarity."""
        try:
            best_match = None
            highest_similarity = 0
            
            # Simple keyword-based matching
            processed_words = set(processed_text.lower().split())
            
            for question_id, question_data in self.questions_cache.items():
                question_text = self._preprocess_text(question_data['text'])
                question_words = set(question_text.lower().split())
                
                # Calculate Jaccard similarity (intersection over union)
                intersection = len(processed_words & question_words)
                union = len(processed_words | question_words)
                
                if union > 0:
                    similarity = intersection / union
                    
                    # Boost similarity if key question words match
                    if self._has_key_word_match(processed_text, question_text):
                        similarity += 0.2
                    
                    if similarity > highest_similarity:
                        highest_similarity = similarity
                        best_match = {
                            'question_id': question_id,
                            'confidence': similarity,
                            'matched_text': question_data['text'],
                            'detected_text': detected_text,
                            'method': 'simple'
                        }
            
            # Lower threshold for simple matching
            simple_threshold = max(0.3, self.similarity_threshold * 0.7)
            if best_match and best_match['confidence'] >= simple_threshold:
                return best_match
            
            return None
            
        except Exception as e:
            print(f"Error in simple matching: {str(e)}")
            return None
    
    def _has_key_word_match(self, text1, text2):
        """Check if texts share key question words."""
        key_words = ['what', 'how', 'when', 'where', 'why', 'who', 'which']
        
        words1 = text1.lower().split()
        words2 = text2.lower().split()
        
        for word in key_words:
            if word in words1 and word in words2:
                return True
        
        return False
    
    def batch_match(self, text_segments):
        """
        Match multiple text segments (useful for processing conversation chunks).
        
        Args:
            text_segments (list): List of text segments to match
            
        Returns:
            list: List of match results
        """
        matches = []
        
        for segment in text_segments:
            match = self.find_best_match(segment)
            if match:
                matches.append(match)
        
        return matches
    
    def update_threshold(self, new_threshold):
        """Update the similarity threshold for matching."""
        self.similarity_threshold = max(0.0, min(1.0, new_threshold))
        print(f"Updated similarity threshold to {self.similarity_threshold}")
    
    def add_question_embedding(self, question_id, question_text):
        """Add a new question and its embedding to the matcher."""
        try:
            if not self.use_simple_matching and self.model:
                # Create embedding using ML model
                embedding = self.model.encode([question_text])[0]
                self.question_embeddings[question_id] = embedding
                print(f"Added ML embedding for: {question_text[:50]}...")
            else:
                print(f"Added question for simple matching: {question_text[:50]}...")
            
            # Always add to cache
            if question_id not in self.questions_cache:
                self.questions_cache[question_id] = {
                    'id': question_id,
                    'text': question_text
                }
            
        except Exception as e:
            print(f"Error adding question embedding: {str(e)}")
            # Don't raise error, just log it
            pass
    
    def remove_question(self, question_id):
        """Remove a question from the matcher."""
        if question_id in self.question_embeddings:
            del self.question_embeddings[question_id]
        if question_id in self.questions_cache:
            del self.questions_cache[question_id]
    
    def save_embeddings(self, file_path):
        """Save embeddings to disk for faster loading."""
        try:
            data = {
                'embeddings': self.question_embeddings,
                'cache': self.questions_cache,
                'threshold': self.similarity_threshold
            }
            
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            
            print(f"Saved embeddings to {file_path}")
            
        except Exception as e:
            print(f"Error saving embeddings: {str(e)}")
            raise e
    
    def load_embeddings(self, file_path):
        """Load embeddings from disk."""
        try:
            if not os.path.exists(file_path):
                print(f"Embeddings file not found: {file_path}")
                return False
            
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            self.question_embeddings = data.get('embeddings', {})
            self.questions_cache = data.get('cache', {})
            self.similarity_threshold = data.get('threshold', 0.7)
            
            print(f"Loaded {len(self.question_embeddings)} embeddings from {file_path}")
            return True
            
        except Exception as e:
            print(f"Error loading embeddings: {str(e)}")
            return False
    
    def get_similar_questions(self, question_text, top_k=5):
        """Get top K similar questions to the given text."""
        try:
            if not self.questions_cache:
                return []
            
            processed_text = self._preprocess_text(question_text)
            
            if not self.use_simple_matching and self.model and self.question_embeddings:
                # Use ML-based similarity
                text_embedding = self.model.encode([processed_text])[0]
                
                similarities = []
                for question_id, question_embedding in self.question_embeddings.items():
                    similarity = cosine_similarity([text_embedding], [question_embedding])[0][0]
                    similarities.append({
                        'question_id': question_id,
                        'text': self.questions_cache[question_id]['text'],
                        'similarity': similarity
                    })
                
                # Sort by similarity and return top K
                similarities.sort(key=lambda x: x['similarity'], reverse=True)
                return similarities[:top_k]
            else:
                # Use simple text-based similarity
                similarities = []
                processed_words = set(processed_text.lower().split())
                
                for question_id, question_data in self.questions_cache.items():
                    question_text_processed = self._preprocess_text(question_data['text'])
                    question_words = set(question_text_processed.lower().split())
                    
                    # Calculate Jaccard similarity
                    intersection = len(processed_words & question_words)
                    union = len(processed_words | question_words)
                    
                    if union > 0:
                        similarity = intersection / union
                        similarities.append({
                            'question_id': question_id,
                            'text': question_data['text'],
                            'similarity': similarity
                        })
                
                # Sort by similarity and return top K
                similarities.sort(key=lambda x: x['similarity'], reverse=True)
                return similarities[:top_k]
            
        except Exception as e:
            print(f"Error getting similar questions: {str(e)}")
            return []
    
    def _preprocess_text(self, text):
        """Preprocess text for better matching."""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove some punctuation but keep question marks
        text = re.sub(r'[^\w\s\?]', '', text)
        
        return text
    
    def _is_likely_question(self, text):
        """Determine if text is likely a question."""
        if not text:
            return False
        
        # Check for question patterns
        for pattern in self.question_patterns:
            if re.search(pattern, text.lower()):
                return True
        
        # Check for question words
        question_words = ['what', 'how', 'when', 'where', 'why', 'who', 'which', 
                         'can', 'could', 'would', 'will', 'do', 'does', 'did',
                         'is', 'are', 'was', 'were', 'have', 'has', 'had']
        
        words = text.lower().split()
        if words and words[0] in question_words:
            return True
        
        # Check for question mark
        if '?' in text:
            return True
        
        return False
    
    def get_stats(self):
        """Get statistics about the question matcher."""
        return {
            'total_questions': len(self.questions_cache),
            'similarity_threshold': self.similarity_threshold,
            'matching_method': 'simple' if self.use_simple_matching else 'ml',
            'model_available': self.model is not None,
            'embeddings_count': len(self.question_embeddings)
        }
