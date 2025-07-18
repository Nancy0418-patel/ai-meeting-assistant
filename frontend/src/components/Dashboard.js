import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  LinearProgress,
  Avatar,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  VideoCall,
  VideoLibrary,
  Quiz,
  TrendingUp,
  PlayCircle,
  Schedule,
  CheckCircle,
  SmartToy,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalRecordings: 0,
    totalQuestions: 0,
    recordedQuestions: 0,
    recentRecordings: [],
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [recordingsRes, questionsRes] = await Promise.all([
        axios.get('/api/recordings'),
        axios.get('/api/questions'),
      ]);

      const recordings = recordingsRes.data;
      const questions = questionsRes.data;
      const recordedQuestionIds = new Set(recordings.map(r => r.question_id));

      setStats({
        totalRecordings: recordings.length,
        totalQuestions: questions.length,
        recordedQuestions: recordedQuestionIds.size,
        recentRecordings: recordings.slice(0, 5),
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const completionPercentage = stats.totalQuestions > 0 
    ? Math.round((stats.recordedQuestions / stats.totalQuestions) * 100) 
    : 0;

  const quickActions = [
    {
      title: 'Start Recording',
      description: 'Record answers to meeting questions',
      icon: <VideoCall />,
      color: '#f44336',
      action: () => navigate('/record'),
    },
    {
      title: 'View Recordings',
      description: 'Browse and manage your recordings',
      icon: <VideoLibrary />,
      color: '#2196f3',
      action: () => navigate('/recordings'),
    },
    {
      title: 'Manage Questions',
      description: 'Add or edit question bank',
      icon: <Quiz />,
      color: '#ff9800',
      action: () => navigate('/questions'),
    },
  ];

  const features = [
    {
      icon: <VideoCall />,
      title: 'Video Recording',
      description: 'Record high-quality video responses to common meeting questions',
    },
    {
      icon: <SmartToy />,
      title: 'AI Matching',
      description: 'Intelligent question detection and response matching during live meetings',
    },
    {
      icon: <PlayCircle />,
      title: 'Real-time Playback',
      description: 'Seamlessly play responses during live meetings as if you\'re present',
    },
  ];

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <LinearProgress sx={{ width: '50%' }} />
      </Box>
    );
  }

  return (
    <Box className="fade-in">
      {/* Welcome Section */}
      <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        <CardContent sx={{ py: 4 }}>
          <Typography variant="h4" gutterBottom fontWeight={600}>
            Welcome to AI Meeting Assistant
          </Typography>
          <Typography variant="h6" sx={{ opacity: 0.9, mb: 3 }}>
            Record your responses once, let AI handle repetitive meeting questions
          </Typography>
          <Box display="flex" gap={2} flexWrap="wrap">
            <Button
              variant="contained"
              size="large"
              startIcon={<VideoCall />}
              onClick={() => navigate('/record')}
              sx={{ 
                bgcolor: 'rgba(255,255,255,0.2)', 
                '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' } 
              }}
            >
              Start Recording
            </Button>
            <Button
              variant="outlined"
              size="large"
              startIcon={<VideoLibrary />}
              onClick={() => navigate('/recordings')}
              sx={{ 
                borderColor: 'rgba(255,255,255,0.5)', 
                color: 'white',
                '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.1)' } 
              }}
            >
              View Recordings
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {/* Stats Cards */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Avatar sx={{ bgcolor: '#2196f3', mr: 2 }}>
                      <VideoLibrary />
                    </Avatar>
                    <Box>
                      <Typography variant="h4" component="div" fontWeight={600}>
                        {stats.totalRecordings}
                      </Typography>
                      <Typography color="text.secondary">
                        Total Recordings
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Avatar sx={{ bgcolor: '#ff9800', mr: 2 }}>
                      <Quiz />
                    </Avatar>
                    <Box>
                      <Typography variant="h4" component="div" fontWeight={600}>
                        {stats.totalQuestions}
                      </Typography>
                      <Typography color="text.secondary">
                        Total Questions
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Avatar sx={{ bgcolor: '#4caf50', mr: 2 }}>
                      <TrendingUp />
                    </Avatar>
                    <Box>
                      <Typography variant="h4" component="div" fontWeight={600}>
                        {completionPercentage}%
                      </Typography>
                      <Typography color="text.secondary">
                        Completion Rate
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Progress Card */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Recording Progress
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {stats.recordedQuestions} of {stats.totalQuestions} questions recorded
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={completionPercentage} 
                    sx={{ height: 8, borderRadius: 4, mb: 2 }}
                  />
                  <Box display="flex" gap={1}>
                    <Chip 
                      icon={<CheckCircle />} 
                      label={`${stats.recordedQuestions} Recorded`} 
                      color="success" 
                      size="small"
                    />
                    <Chip 
                      icon={<Schedule />} 
                      label={`${stats.totalQuestions - stats.recordedQuestions} Remaining`} 
                      color="warning" 
                      size="small"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: 'fit-content' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <List dense>
                {quickActions.map((action, index) => (
                  <ListItem 
                    key={index}
                    button
                    onClick={action.action}
                    sx={{ borderRadius: 1, mb: 1 }}
                  >
                    <ListItemIcon>
                      <Avatar sx={{ bgcolor: action.color, width: 32, height: 32 }}>
                        {action.icon}
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText
                      primary={action.title}
                      secondary={action.description}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Features Overview */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Key Features
              </Typography>
              <Grid container spacing={3}>
                {features.map((feature, index) => (
                  <Grid item xs={12} md={4} key={index}>
                    <Box textAlign="center">
                      <Box className="feature-icon">
                        {feature.icon}
                      </Box>
                      <Typography variant="h6" gutterBottom>
                        {feature.title}
                      </Typography>
                      <Typography color="text.secondary">
                        {feature.description}
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Recordings */}
        {stats.recentRecordings.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Recordings
                </Typography>
                <List>
                  {stats.recentRecordings.map((recording, index) => (
                    <React.Fragment key={recording.id}>
                      <ListItem>
                        <ListItemIcon>
                          <PlayCircle color="primary" />
                        </ListItemIcon>
                        <ListItemText
                          primary={recording.question_text}
                          secondary={`Recorded ${new Date(recording.created_at).toLocaleDateString()}`}
                        />
                        <Chip 
                          label={`${Math.round(recording.duration)}s`} 
                          size="small" 
                          variant="outlined"
                        />
                      </ListItem>
                      {index < stats.recentRecordings.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
                <Box mt={2}>
                  <Button 
                    variant="outlined" 
                    onClick={() => navigate('/recordings')}
                    fullWidth
                  >
                    View All Recordings
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}

export default Dashboard;
