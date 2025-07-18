import React, { useState, useRef } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  Chip,
  Grid,
  Paper,
} from '@mui/material';
import {
  Mic,
  MicOff,
  Upload,
  PlayArrow,
  Stop,
  CheckCircle,
  Error,
} from '@mui/icons-material';
import axios from 'axios';
import { toast } from 'react-toastify';

function SpeechToTextTest() {
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [selectedService, setSelectedService] = useState('gemini');
  const [serviceStatus, setServiceStatus] = useState({});
  const [audioFile, setAudioFile] = useState(null);
  const fileInputRef = useRef(null);

  const services = [
    { value: 'openai', label: 'OpenAI Whisper (Recommended)' },
    { value: 'gemini', label: 'Google Gemini (Free Tier Available)' },
    { value: 'google', label: 'Google Speech Recognition' },
    { value: 'azure', label: 'Azure Speech Services' },
    { value: 'deepgram', label: 'Deepgram' },
    { value: 'assemblyai', label: 'AssemblyAI' },
    { value: 'offline', label: 'Offline Recognition' },
  ];

  const testServices = async () => {
    try {
      setIsTranscribing(true);
      const response = await axios.get('/api/speech-to-text/test');
      setServiceStatus(response.data.services);
      toast.success('Service test completed');
    } catch (error) {
      console.error('Error testing services:', error);
      toast.error('Failed to test services');
    } finally {
      setIsTranscribing(false);
    }
  };

  const startLiveTranscription = async () => {
    try {
      setIsRecording(true);
      setIsTranscribing(true);
      setTranscription('');
      
      const response = await axios.post('/api/speech-to-text/live', {
        duration: 10, // 10 seconds
        service: selectedService
      });
      
      if (response.data.transcription.text) {
        setTranscription(response.data.transcription.text);
        toast.success('Transcription completed');
      } else {
        toast.warning('No speech detected');
      }
    } catch (error) {
      console.error('Error with live transcription:', error);
      toast.error('Failed to transcribe audio');
    } finally {
      setIsRecording(false);
      setIsTranscribing(false);
    }
  };

  const uploadAndTranscribe = async () => {
    if (!audioFile) {
      toast.warning('Please select an audio file');
      return;
    }

    try {
      setIsTranscribing(true);
      const formData = new FormData();
      formData.append('audio', audioFile);
      formData.append('service', selectedService);

      const response = await axios.post('/api/speech-to-text/transcribe', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.transcription.text) {
        setTranscription(response.data.transcription.text);
        toast.success('File transcribed successfully');
      } else {
        toast.warning('No speech detected in file');
      }
    } catch (error) {
      console.error('Error transcribing file:', error);
      toast.error('Failed to transcribe file');
    } finally {
      setIsTranscribing(false);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setAudioFile(file);
    }
  };

  const renderServiceStatus = (service, status) => {
    const serviceInfo = services.find(s => s.value === service);
    return (
      <Grid item xs={12} sm={6} md={4} key={service}>
        <Paper sx={{ p: 2, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>
            {serviceInfo?.label || service}
          </Typography>
          {status.available ? (
            <Chip
              icon={<CheckCircle />}
              label="Available"
              color="success"
              variant="outlined"
            />
          ) : (
            <Chip
              icon={<Error />}
              label="Not Available"
              color="error"
              variant="outlined"
            />
          )}
          {status.error && (
            <Typography variant="caption" color="error" sx={{ mt: 1, display: 'block' }}>
              {status.error}
            </Typography>
          )}
        </Paper>
      </Grid>
    );
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Speech-to-Text Testing
      </Typography>

      {/* Service Selection */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Select Speech-to-Text Service
          </Typography>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Service</InputLabel>
            <Select
              value={selectedService}
              onChange={(e) => setSelectedService(e.target.value)}
              label="Service"
            >
              {services.map((service) => (
                <MenuItem key={service.value} value={service.value}>
                  {service.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Button
            variant="outlined"
            onClick={testServices}
            disabled={isTranscribing}
            startIcon={isTranscribing ? <CircularProgress size={16} /> : <CheckCircle />}
          >
            Test All Services
          </Button>
        </CardContent>
      </Card>

      {/* Service Status */}
      {Object.keys(serviceStatus).length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Service Status
            </Typography>
            <Grid container spacing={2}>
              {Object.entries(serviceStatus).map(([service, status]) =>
                renderServiceStatus(service, status)
              )}
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Live Recording */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Live Recording
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Click to record 10 seconds of audio from your microphone
          </Typography>
          <Button
            variant="contained"
            color={isRecording ? 'secondary' : 'primary'}
            size="large"
            onClick={startLiveTranscription}
            disabled={isTranscribing}
            startIcon={
              isTranscribing ? (
                <CircularProgress size={20} />
              ) : isRecording ? (
                <MicOff />
              ) : (
                <Mic />
              )
            }
          >
            {isTranscribing ? 'Transcribing...' : isRecording ? 'Recording...' : 'Start Recording'}
          </Button>
        </CardContent>
      </Card>

      {/* File Upload */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Upload Audio File
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Upload an audio file (WAV, MP3, M4A, etc.) to transcribe
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <input
              type="file"
              accept="audio/*"
              onChange={handleFileSelect}
              ref={fileInputRef}
              style={{ display: 'none' }}
            />
            <Button
              variant="outlined"
              onClick={() => fileInputRef.current?.click()}
              startIcon={<Upload />}
            >
              Select File
            </Button>
            {audioFile && (
              <Chip
                label={audioFile.name}
                onDelete={() => setAudioFile(null)}
                color="primary"
              />
            )}
            <Button
              variant="contained"
              onClick={uploadAndTranscribe}
              disabled={!audioFile || isTranscribing}
              startIcon={isTranscribing ? <CircularProgress size={16} /> : <PlayArrow />}
            >
              Transcribe File
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Transcription Results */}
      {transcription && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Transcription Result
            </Typography>
            <Paper sx={{ p: 2, bgcolor: 'grey.100', minHeight: 100 }}>
              <Typography variant="body1">
                {transcription}
              </Typography>
            </Paper>
          </CardContent>
        </Card>
      )}

      {/* Setup Instructions */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Setup Instructions
          </Typography>
          <Alert severity="info" sx={{ mb: 2 }}>
            To use speech-to-text services, you need to set up API keys in your .env file
          </Alert>
          <Typography variant="body2">
            <strong>Quick Start:</strong>
            <br />
            1. Create a `.env` file in the backend folder
            <br />
            2. Add your API keys (start with OpenAI for best results)
            <br />
            3. Restart the backend server
            <br />
            4. Test the services using the buttons above
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}

export default SpeechToTextTest;
