import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
} from '@mui/material';
import {
  Add,
  Quiz,
  Delete,
  Edit,
  VideoCall,
} from '@mui/icons-material';
import axios from 'axios';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';

function QuestionBank() {
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([]);
  const [recordings, setRecordings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [newQuestion, setNewQuestion] = useState({
    text: '',
    category: 'general',
  });

  const categories = [
    { value: 'general', label: 'General' },
    { value: 'project', label: 'Project Updates' },
    { value: 'status', label: 'Status Reports' },
    { value: 'planning', label: 'Planning' },
    { value: 'feedback', label: 'Feedback' },
    { value: 'technical', label: 'Technical' },
    { value: 'custom', label: 'Custom' },
  ];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [questionsRes, recordingsRes] = await Promise.all([
        axios.get('/api/questions'),
        axios.get('/api/recordings'),
      ]);
      
      setQuestions(questionsRes.data);
      setRecordings(recordingsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleAddQuestion = async () => {
    if (!newQuestion.text.trim()) {
      toast.warning('Please enter a question');
      return;
    }

    try {
      const response = await axios.post('/api/questions', newQuestion);
      setQuestions(prev => [...prev, response.data]);
      setNewQuestion({ text: '', category: 'general' });
      setAddDialogOpen(false);
      toast.success('Question added successfully');
    } catch (error) {
      console.error('Error adding question:', error);
      toast.error('Failed to add question');
    }
  };

  const handleRecordAnswer = (questionId) => {
    navigate(`/record?question=${questionId}`);
  };

  const getQuestionStats = () => {
    const recordedQuestionIds = new Set(recordings.map(r => r.question_id));
    const total = questions.length;
    const recorded = recordedQuestionIds.size;
    const pending = total - recorded;

    return { total, recorded, pending };
  };

  const isQuestionRecorded = (questionId) => {
    return recordings.some(r => r.question_id === questionId);
  };

  const getQuestionsByCategory = () => {
    const grouped = {};
    questions.forEach(question => {
      const category = question.category || 'general';
      if (!grouped[category]) {
        grouped[category] = [];
      }
      grouped[category].push(question);
    });
    return grouped;
  };

  const stats = getQuestionStats();
  const questionsByCategory = getQuestionsByCategory();

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Loading questions...</Typography>
      </Box>
    );
  }

  return (
    <Box className="fade-in">
      {/* Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Box>
              <Typography variant="h5" gutterBottom fontWeight={600}>
                Question Bank
              </Typography>
              <Typography color="text.secondary">
                Manage meeting questions and track recording progress
              </Typography>
            </Box>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setAddDialogOpen(true)}
            >
              Add Question
            </Button>
          </Box>

          {/* Stats */}
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <Box textAlign="center" p={2} bgcolor="primary.main" color="white" borderRadius={2}>
                <Typography variant="h4" fontWeight={600}>
                  {stats.total}
                </Typography>
                <Typography variant="body2">
                  Total Questions
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box textAlign="center" p={2} bgcolor="success.main" color="white" borderRadius={2}>
                <Typography variant="h4" fontWeight={600}>
                  {stats.recorded}
                </Typography>
                <Typography variant="body2">
                  Recorded
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box textAlign="center" p={2} bgcolor="warning.main" color="white" borderRadius={2}>
                <Typography variant="h4" fontWeight={600}>
                  {stats.pending}
                </Typography>
                <Typography variant="body2">
                  Pending
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Questions by Category */}
      {Object.entries(questionsByCategory).map(([category, categoryQuestions]) => (
        <Card key={category} sx={{ mb: 3 }}>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <Typography variant="h6" sx={{ textTransform: 'capitalize', fontWeight: 600 }}>
                {categories.find(c => c.value === category)?.label || category}
              </Typography>
              <Chip 
                label={categoryQuestions.length} 
                size="small" 
                sx={{ ml: 2 }}
              />
            </Box>

            <List>
              {categoryQuestions.map((question, index) => (
                <React.Fragment key={question.id}>
                  <ListItem>
                    <ListItemText
                      primary={question.text}
                      secondary={
                        <Box display="flex" alignItems="center" gap={1} mt={1}>
                          {question.is_default && (
                            <Chip label="Default" size="small" color="secondary" />
                          )}
                          {isQuestionRecorded(question.id) ? (
                            <Chip 
                              label="Recorded" 
                              size="small" 
                              color="success"
                              icon={<VideoCall />}
                            />
                          ) : (
                            <Chip 
                              label="Not Recorded" 
                              size="small" 
                              color="warning"
                            />
                          )}
                          <Typography variant="caption" color="text.secondary">
                            Added {new Date(question.created_at).toLocaleDateString()}
                          </Typography>
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Button
                        size="small"
                        variant={isQuestionRecorded(question.id) ? "outlined" : "contained"}
                        startIcon={<VideoCall />}
                        onClick={() => handleRecordAnswer(question.id)}
                        sx={{ mr: 1 }}
                      >
                        {isQuestionRecorded(question.id) ? 'Re-record' : 'Record'}
                      </Button>
                      {!question.is_default && (
                        <>
                          <IconButton
                            size="small"
                            onClick={() => {
                              setSelectedQuestion(question);
                              setEditDialogOpen(true);
                            }}
                          >
                            <Edit />
                          </IconButton>
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => {
                              // Add delete functionality here
                            }}
                          >
                            <Delete />
                          </IconButton>
                        </>
                      )}
                    </ListItemSecondaryAction>
                  </ListItem>
                  {index < categoryQuestions.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </CardContent>
        </Card>
      ))}

      {questions.length === 0 && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <Quiz sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No questions yet
            </Typography>
            <Typography color="text.secondary" gutterBottom>
              Add your first meeting question to get started
            </Typography>
            <Button 
              variant="contained" 
              startIcon={<Add />}
              onClick={() => setAddDialogOpen(true)}
              sx={{ mt: 2 }}
            >
              Add Question
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Add Question Dialog */}
      <Dialog open={addDialogOpen} onClose={() => setAddDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Question</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Question Text"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={newQuestion.text}
            onChange={(e) => setNewQuestion(prev => ({ ...prev, text: e.target.value }))}
            placeholder="e.g., What's your opinion on this proposal?"
            sx={{ mb: 2 }}
          />
          <FormControl fullWidth>
            <InputLabel>Category</InputLabel>
            <Select
              value={newQuestion.category}
              label="Category"
              onChange={(e) => setNewQuestion(prev => ({ ...prev, category: e.target.value }))}
            >
              {categories.map((category) => (
                <MenuItem key={category.value} value={category.value}>
                  {category.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleAddQuestion} variant="contained">
            Add Question
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Question Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Question</DialogTitle>
        <DialogContent>
          {selectedQuestion && (
            <>
              <TextField
                autoFocus
                margin="dense"
                label="Question Text"
                fullWidth
                multiline
                rows={3}
                variant="outlined"
                defaultValue={selectedQuestion.text}
                sx={{ mb: 2 }}
              />
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  defaultValue={selectedQuestion.category}
                  label="Category"
                >
                  {categories.map((category) => (
                    <MenuItem key={category.value} value={category.value}>
                      {category.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button variant="contained">
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default QuestionBank;
