import React, { useState, useEffect, useRef } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Alert,
  LinearProgress,
  Chip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  VideoCall,
  Stop,
  PlayArrow,
  Pause,
  Refresh,
  CloudUpload,
  CheckCircle,
  Timer,
} from '@mui/icons-material';
import Webcam from 'react-webcam';
import RecordRTC from 'recordrtc';
import axios from 'axios';
import { toast } from 'react-toastify';

const RECORDING_CONSTRAINTS = {
  video: {
    width: { ideal: 1280 },
    height: { ideal: 720 },
    frameRate: { ideal: 30 }
  },
  audio: {
    sampleRate: 44100,
    channelCount: 2,
    volume: 1.0
  }
};

function RecordingStudio() {
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [questions, setQuestions] = useState([]);
  const [selectedQuestion, setSelectedQuestion] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [showPreview, setShowPreview] = useState(false);
  const [cameraReady, setCameraReady] = useState(false);
  const timerRef = useRef(null);

  useEffect(() => {
    fetchQuestions();
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  const fetchQuestions = async () => {
    try {
      const response = await axios.get('/api/questions');
      setQuestions(response.data);
    } catch (error) {
      console.error('Error fetching questions:', error);
      toast.error('Failed to load questions');
    }
  };

  const startRecording = async () => {
    try {
      if (!selectedQuestion) {
        toast.warning('Please select a question first');
        return;
      }

      const stream = webcamRef.current.stream;
      if (!stream) {
        toast.error('Camera not ready');
        return;
      }

      // Initialize RecordRTC
      mediaRecorderRef.current = new RecordRTC(stream, {
        type: 'video',
        mimeType: 'video/webm',
        videoBitsPerSecond: 2000000, // 2Mbps
        audioBitsPerSecond: 128000,  // 128kbps
        canvas: {
          width: 1280,
          height: 720
        }
      });

      mediaRecorderRef.current.startRecording();
      setIsRecording(true);
      setRecordingTime(0);

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

      toast.success('Recording started');
    } catch (error) {
      console.error('Error starting recording:', error);
      toast.error('Failed to start recording');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stopRecording(() => {
        const blob = mediaRecorderRef.current.getBlob();
        setRecordedBlob(blob);
        setPreviewUrl(URL.createObjectURL(blob));
        setShowPreview(true);
      });

      setIsRecording(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }

      toast.success('Recording stopped');
    }
  };

  const uploadRecording = async () => {
    if (!recordedBlob || !selectedQuestion) {
      toast.error('No recording or question selected');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('video', recordedBlob, `recording_${Date.now()}.webm`);
      formData.append('question_id', selectedQuestion);

      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(progress);
        },
      });

      toast.success('Recording uploaded successfully!');
      resetRecording();
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to upload recording');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const resetRecording = () => {
    setRecordedBlob(null);
    setPreviewUrl(null);
    setRecordingTime(0);
    setShowPreview(false);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const selectedQuestionData = questions.find(q => q.id.toString() === selectedQuestion);

  return (
    <Box className="fade-in">
      <Grid container spacing={3}>
        {/* Question Selection */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom fontWeight={600}>
                Recording Studio
              </Typography>
              <Typography color="text.secondary" gutterBottom>
                Select a question and record your response
              </Typography>
              
              <FormControl fullWidth sx={{ mt: 2 }}>
                <InputLabel>Select Question</InputLabel>
                <Select
                  value={selectedQuestion}
                  onChange={(e) => setSelectedQuestion(e.target.value)}
                  label="Select Question"
                >
                  {questions.map((question) => (
                    <MenuItem key={question.id} value={question.id.toString()}>
                      {question.text}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {selectedQuestionData && (
                <Box mt={2}>
                  <Chip 
                    label={selectedQuestionData.category} 
                    color="primary" 
                    size="small"
                  />
                  {selectedQuestionData.is_default && (
                    <Chip 
                      label="Default" 
                      color="secondary" 
                      size="small" 
                      sx={{ ml: 1 }}
                    />
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Camera View */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Camera View
              </Typography>
              
              <Box className="video-container" sx={{ position: 'relative', mb: 2 }}>
                <Webcam
                  ref={webcamRef}
                  audio={true}
                  videoConstraints={RECORDING_CONSTRAINTS.video}
                  audioConstraints={RECORDING_CONSTRAINTS.audio}
                  onUserMedia={() => setCameraReady(true)}
                  onUserMediaError={(error) => {
                    console.error('Camera error:', error);
                    toast.error('Failed to access camera');
                  }}
                  style={{
                    width: '100%',
                    height: 'auto',
                    borderRadius: '12px',
                  }}
                />
                
                {isRecording && (
                  <Box className="recording-indicator">
                    <Timer sx={{ fontSize: 16 }} />
                    REC {formatTime(recordingTime)}
                  </Box>
                )}
              </Box>

              <Box display="flex" gap={2} justifyContent="center" flexWrap="wrap">
                <Button
                  variant="contained"
                  color="error"
                  size="large"
                  startIcon={isRecording ? <Stop /> : <VideoCall />}
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={!cameraReady || !selectedQuestion}
                  sx={{ minWidth: 140 }}
                >
                  {isRecording ? 'Stop Recording' : 'Start Recording'}
                </Button>

                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={resetRecording}
                  disabled={isRecording || !recordedBlob}
                >
                  Reset
                </Button>

                <Button
                  variant="contained"
                  color="success"
                  startIcon={<CloudUpload />}
                  onClick={uploadRecording}
                  disabled={!recordedBlob || isUploading}
                  sx={{ minWidth: 120 }}
                >
                  {isUploading ? 'Uploading...' : 'Upload'}
                </Button>
              </Box>

              {isUploading && (
                <Box mt={2}>
                  <Typography variant="body2" gutterBottom>
                    Upload Progress: {uploadProgress}%
                  </Typography>
                  <LinearProgress variant="determinate" value={uploadProgress} />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recording Status */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recording Status
              </Typography>
              
              <Box mb={2}>
                <Alert 
                  severity={cameraReady ? 'success' : 'warning'} 
                  icon={cameraReady ? <CheckCircle /> : <Timer />}
                >
                  Camera: {cameraReady ? 'Ready' : 'Initializing...'}
                </Alert>
              </Box>

              <Box mb={2}>
                <Alert 
                  severity={selectedQuestion ? 'success' : 'info'} 
                  icon={selectedQuestion ? <CheckCircle /> : <Timer />}
                >
                  Question: {selectedQuestion ? 'Selected' : 'Please select a question'}
                </Alert>
              </Box>

              {isRecording && (
                <Box mb={2}>
                  <Alert severity="error" icon={<Timer />}>
                    Recording: {formatTime(recordingTime)}
                  </Alert>
                </Box>
              )}

              {recordedBlob && (
                <Box mb={2}>
                  <Alert severity="success" icon={<CheckCircle />}>
                    Recording captured ({Math.round(recordedBlob.size / 1024 / 1024 * 100) / 100} MB)
                  </Alert>
                </Box>
              )}

              <Typography variant="body2" color="text.secondary">
                Tips:
                <br />• Ensure good lighting
                <br />• Speak clearly and at normal pace
                <br />• Keep recordings under 5 minutes
                <br />• Test your audio levels
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Preview Dialog */}
      <Dialog 
        open={showPreview} 
        onClose={() => setShowPreview(false)}
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          Recording Preview
        </DialogTitle>
        <DialogContent>
          {previewUrl && (
            <Box className="video-container">
              <video 
                src={previewUrl} 
                controls 
                style={{ width: '100%', height: 'auto' }}
              />
            </Box>
          )}
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Question: {selectedQuestionData?.text}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPreview(false)}>
            Close
          </Button>
          <Button onClick={resetRecording} color="warning">
            Re-record
          </Button>
          <Button onClick={uploadRecording} variant="contained" disabled={isUploading}>
            Upload Recording
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default RecordingStudio;
