import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Container, AppBar, Toolbar, Typography, Box } from '@mui/material';
import { VideoCall, SmartToy } from '@mui/icons-material';
import Dashboard from './components/Dashboard';
import RecordingStudio from './components/RecordingStudio';
import RecordingsList from './components/RecordingsList';
import QuestionBank from './components/QuestionBank';
import SpeechToTextTest from './components/SpeechToTextTest';
import Navigation from './components/Navigation';

function App() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" elevation={0} sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
        <Toolbar>
          <SmartToy sx={{ mr: 2, fontSize: 28 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            AI Meeting Assistant
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            Record • Train • Automate
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 3, mb: 4 }}>
        <Navigation />
        
        <Box sx={{ mt: 3 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/record" element={<RecordingStudio />} />
            <Route path="/recordings" element={<RecordingsList />} />
            <Route path="/questions" element={<QuestionBank />} />
            <Route path="/speech-test" element={<SpeechToTextTest />} />
          </Routes>
        </Box>
      </Container>
    </Box>
  );
}

export default App;
