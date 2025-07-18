import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Box,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Menu,
  MenuItem,
  Avatar,
} from '@mui/material';
import {
  PlayArrow,
  Delete,
  MoreVert,
  VideoLibrary,
  Schedule,
  Visibility,
} from '@mui/icons-material';
import axios from 'axios';
import { toast } from 'react-toastify';

function RecordingsList() {
  const [recordings, setRecordings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRecording, setSelectedRecording] = useState(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [menuAnchorEl, setMenuAnchorEl] = useState(null);
  const [selectedMenuRecording, setSelectedMenuRecording] = useState(null);

  useEffect(() => {
    fetchRecordings();
  }, []);

  const fetchRecordings = async () => {
    try {
      const response = await axios.get('/api/recordings');
      setRecordings(response.data);
    } catch (error) {
      console.error('Error fetching recordings:', error);
      toast.error('Failed to load recordings');
    } finally {
      setLoading(false);
    }
  };

  const handlePlayRecording = (recording) => {
    setSelectedRecording(recording);
    setPreviewOpen(true);
  };

  const handleDeleteRecording = async (recordingId) => {
    try {
      await axios.delete(`/api/recordings/${recordingId}`);
      setRecordings(prev => prev.filter(r => r.id !== recordingId));
      toast.success('Recording deleted successfully');
      setDeleteConfirmOpen(false);
    } catch (error) {
      console.error('Error deleting recording:', error);
      toast.error('Failed to delete recording');
    }
  };

  const handleMenuOpen = (event, recording) => {
    setMenuAnchorEl(event.currentTarget);
    setSelectedMenuRecording(recording);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
    setSelectedMenuRecording(null);
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024 * 1024) {
      return `${Math.round(bytes / 1024)} KB`;
    }
    return `${Math.round(bytes / 1024 / 1024 * 10) / 10} MB`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Loading recordings...</Typography>
      </Box>
    );
  }

  return (
    <Box className="fade-in">
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom fontWeight={600}>
            My Recordings
          </Typography>
          <Typography color="text.secondary">
            Manage and view your recorded responses ({recordings.length} total)
          </Typography>
        </CardContent>
      </Card>

      {recordings.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <VideoLibrary sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No recordings yet
            </Typography>
            <Typography color="text.secondary" gutterBottom>
              Start by recording answers to common meeting questions
            </Typography>
            <Button 
              variant="contained" 
              href="/record"
              sx={{ mt: 2 }}
            >
              Start Recording
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {recordings.map((recording) => (
            <Grid item xs={12} sm={6} lg={4} key={recording.id}>
              <Card className="question-card">
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                    <Avatar sx={{ bgcolor: 'primary.main', width: 40, height: 40 }}>
                      <VideoLibrary />
                    </Avatar>
                    <IconButton 
                      size="small"
                      onClick={(e) => handleMenuOpen(e, recording)}
                    >
                      <MoreVert />
                    </IconButton>
                  </Box>

                  <Typography variant="h6" gutterBottom noWrap>
                    {recording.question_text}
                  </Typography>

                  <Box display="flex" gap={1} mb={2}>
                    <Chip 
                      icon={<Schedule />}
                      label={formatDuration(recording.duration)}
                      size="small"
                      variant="outlined"
                    />
                    <Chip 
                      label={formatFileSize(recording.file_size)}
                      size="small"
                      variant="outlined"
                    />
                  </Box>

                  <Typography variant="body2" color="text.secondary">
                    Recorded {formatDate(recording.created_at)}
                  </Typography>
                </CardContent>

                <CardActions>
                  <Button
                    size="small"
                    startIcon={<PlayArrow />}
                    onClick={() => handlePlayRecording(recording)}
                  >
                    Preview
                  </Button>
                  <Button
                    size="small"
                    startIcon={<Visibility />}
                    href={`/api/recordings/${recording.id}/play`}
                    target="_blank"
                  >
                    View
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Context Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => {
          handlePlayRecording(selectedMenuRecording);
          handleMenuClose();
        }}>
          <PlayArrow sx={{ mr: 1 }} />
          Preview
        </MenuItem>
        <MenuItem onClick={() => {
          window.open(`/api/recordings/${selectedMenuRecording?.id}/play`, '_blank');
          handleMenuClose();
        }}>
          <Visibility sx={{ mr: 1 }} />
          Open in New Tab
        </MenuItem>
        <MenuItem 
          onClick={() => {
            setSelectedRecording(selectedMenuRecording);
            setDeleteConfirmOpen(true);
            handleMenuClose();
          }}
          sx={{ color: 'error.main' }}
        >
          <Delete sx={{ mr: 1 }} />
          Delete
        </MenuItem>
      </Menu>

      {/* Preview Dialog */}
      <Dialog 
        open={previewOpen} 
        onClose={() => setPreviewOpen(false)}
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          Recording Preview
        </DialogTitle>
        <DialogContent>
          {selectedRecording && (
            <>
              <Box className="video-container" sx={{ mb: 2 }}>
                <video 
                  src={`/api/recordings/${selectedRecording.id}/play`}
                  controls 
                  style={{ width: '100%', height: 'auto' }}
                  autoPlay
                />
              </Box>
              <Typography variant="body1" gutterBottom>
                <strong>Question:</strong> {selectedRecording.question_text}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Duration: {formatDuration(selectedRecording.duration)} • 
                Size: {formatFileSize(selectedRecording.file_size)} • 
                Recorded: {formatDate(selectedRecording.created_at)}
              </Typography>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Delete Recording
        </DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this recording? This action cannot be undone.
          </Typography>
          {selectedRecording && (
            <Box mt={2} p={2} bgcolor="grey.100" borderRadius={1}>
              <Typography variant="body2">
                <strong>Question:</strong> {selectedRecording.question_text}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Duration: {formatDuration(selectedRecording.duration)}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirmOpen(false)}>
            Cancel
          </Button>
          <Button 
            onClick={() => handleDeleteRecording(selectedRecording?.id)}
            color="error"
            variant="contained"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default RecordingsList;
