import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Slider,
  Alert,
  Snackbar,
  Avatar,
  Chip,
  Paper,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Rating,
  Tabs,
  Tab,
} from '@mui/material';
import { Send, CheckCircle, Person, Psychology } from '@mui/icons-material';

// Mock data
const teammates = [
  { id: 1, name: 'Jamie Brown', department: 'Engineering', role: 'Senior Developer', avatar: 'JB' },
  { id: 2, name: 'Quinn Davis', department: 'Product', role: 'Product Manager', avatar: 'QD' },
  { id: 3, name: 'River Anderson', department: 'Design', role: 'UX Designer', avatar: 'RA' },
  { id: 4, name: 'Casey Garcia', department: 'Marketing', role: 'Marketing Manager', avatar: 'CG' },
  { id: 5, name: 'Taylor Johnson', department: 'Operations', role: 'Operations Lead', avatar: 'TJ' },
];

const descriptors = [
  { value: 'collaborative', label: '🤝 Collaborative', description: 'Works well with others, shares knowledge' },
  { value: 'neutral', label: '😐 Neutral', description: 'Standard interaction level' },
  { value: 'withdrawn', label: '😔 Withdrawn', description: 'Less engaged, keeps to themselves' },
  { value: 'blocking', label: '🚫 Blocking', description: 'Creates obstacles, difficult to work with' },
];

const recentReviews = [
  { id: 1, reviewee: 'Jamie Brown', descriptor: 'Collaborative', score: 5, date: '2024-01-15', status: 'submitted' },
  { id: 2, reviewee: 'Quinn Davis', descriptor: 'Neutral', score: 3, date: '2024-01-14', status: 'submitted' },
  { id: 3, reviewee: 'River Anderson', descriptor: 'Collaborative', score: 4, date: '2024-01-13', status: 'submitted' },
];

export default function Reviews() {
  const [tabValue, setTabValue] = useState(0);
  const [selectedReviewee, setSelectedReviewee] = useState('');
  const [descriptor, setDescriptor] = useState('');
  const [score, setScore] = useState<number | null>(4);
  const [comment, setComment] = useState('');
  const [showSuccess, setShowSuccess] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedReviewee || !descriptor) {
      return;
    }

    // Simulate API call
    setTimeout(() => {
      setShowSuccess(true);
      // Reset form
      setSelectedReviewee('');
      setDescriptor('');
      setScore(4);
      setComment('');
    }, 500);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
          Peer Reviews
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Share feedback and rate your colleagues' collaboration and performance
        </Typography>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Submit Review" />
          <Tab label="My Reviews" />
          <Tab label="AI Insights" />
        </Tabs>
      </Box>

      {/* Submit Review Tab */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          {/* Review Form */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent sx={{ p: 4 }}>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Person />
                  Submit a Peer Review
                </Typography>
                
                <form onSubmit={handleSubmit}>
                  <Grid container spacing={3}>
                    {/* Select Reviewee */}
                    <Grid item xs={12}>
                      <FormControl fullWidth>
                        <InputLabel>Select Colleague</InputLabel>
                        <Select
                          value={selectedReviewee}
                          label="Select Colleague"
                          onChange={(e) => setSelectedReviewee(e.target.value)}
                          required
                        >
                          {teammates.map((teammate) => (
                            <MenuItem key={teammate.id} value={teammate.name}>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                <Avatar sx={{ width: 32, height: 32 }}>{teammate.avatar}</Avatar>
                                <Box>
                                  <Typography variant="body2">{teammate.name}</Typography>
                                  <Typography variant="caption" color="text.secondary">
                                    {teammate.role} • {teammate.department}
                                  </Typography>
                                </Box>
                              </Box>
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>

                    {/* Descriptor */}
                    <Grid item xs={12}>
                      <FormControl fullWidth>
                        <InputLabel>Collaboration Style</InputLabel>
                        <Select
                          value={descriptor}
                          label="Collaboration Style"
                          onChange={(e) => setDescriptor(e.target.value)}
                          required
                        >
                          {descriptors.map((desc) => (
                            <MenuItem key={desc.value} value={desc.value}>
                              <Box>
                                <Typography variant="body2">{desc.label}</Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {desc.description}
                                </Typography>
                              </Box>
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>

                    {/* Rating */}
                    <Grid item xs={12}>
                      <Typography variant="body2" gutterBottom>
                        Overall Performance Rating
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Rating
                          value={score}
                          onChange={(event, newValue) => setScore(newValue)}
                          size="large"
                        />
                        <Typography variant="body2" color="text.secondary">
                          {score}/5
                        </Typography>
                      </Box>
                    </Grid>

                    {/* Comment */}
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Additional Comments (Optional)"
                        multiline
                        rows={4}
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        placeholder="Share specific examples or constructive feedback..."
                      />
                    </Grid>

                    {/* Submit Button */}
                    <Grid item xs={12}>
                      <Button
                        type="submit"
                        variant="contained"
                        size="large"
                        startIcon={<Send />}
                        sx={{ 
                          background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                          px: 4,
                          py: 1.5,
                        }}
                      >
                        Submit Review
                      </Button>
                    </Grid>
                  </Grid>
                </form>
              </CardContent>
            </Card>
          </Grid>

          {/* Guidelines */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  📋 Review Guidelines
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText
                      primary="Be Constructive"
                      secondary="Focus on behaviors and specific examples"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Stay Professional"
                      secondary="Keep feedback work-related and respectful"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Be Honest"
                      secondary="Authentic feedback helps everyone grow"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Regular Updates"
                      secondary="Submit reviews weekly for best insights"
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>

            <Alert severity="info" sx={{ mt: 2 }}>
              💡 <strong>Pro Tip:</strong> Regular, specific feedback helps our AI provide better insights for team development.
            </Alert>
          </Grid>
        </Grid>
      )}

      {/* My Reviews Tab */}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  📝 Recent Reviews Submitted
                </Typography>
                <List>
                  {recentReviews.map((review, index) => (
                    <ListItem key={review.id} divider={index < recentReviews.length - 1}>
                      <ListItemAvatar>
                        <Avatar>{review.reviewee.split(' ').map(n => n[0]).join('')}</Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="subtitle2">{review.reviewee}</Typography>
                            <Chip 
                              label={review.descriptor} 
                              size="small" 
                              color={review.descriptor === 'Collaborative' ? 'success' : 'default'}
                            />
                            <Rating value={review.score} size="small" readOnly />
                          </Box>
                        }
                        secondary={`Submitted on ${new Date(review.date).toLocaleDateString()}`}
                      />
                      <Chip 
                        label={review.status === 'submitted' ? 'Submitted' : 'Draft'}
                        color={review.status === 'submitted' ? 'success' : 'warning'}
                        icon={review.status === 'submitted' ? <CheckCircle /> : undefined}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* AI Insights Tab */}
      {tabValue === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Psychology color="primary" />
                  AI-Powered Review Insights
                </Typography>
                
                <Alert severity="info" sx={{ mb: 3 }}>
                  🧠 Based on your review patterns, here are some AI-generated insights about your feedback style
                </Alert>

                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 3, background: 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)' }}>
                      <Typography variant="h6" gutterBottom>
                        Your Feedback Style
                      </Typography>
                      <Typography variant="body2" paragraph>
                        📊 You tend to give balanced, constructive feedback with an average rating of 4.2/5. 
                        Your reviews show attention to both strengths and areas for improvement.
                      </Typography>
                      <Chip label="Balanced Reviewer" color="primary" />
                    </Paper>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 3, background: 'linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%)' }}>
                      <Typography variant="h6" gutterBottom>
                        Team Impact
                      </Typography>
                      <Typography variant="body2" paragraph>
                        🎯 Your feedback has helped identify 3 team members who could benefit from 
                        additional collaboration training and mentoring.
                      </Typography>
                      <Chip label="High Impact" color="secondary" />
                    </Paper>
                  </Grid>

                  <Grid item xs={12}>
                    <Paper sx={{ p: 3, background: 'linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%)' }}>
                      <Typography variant="h6" gutterBottom>
                        💡 AI Recommendations
                      </Typography>
                      <Typography variant="body2" paragraph>
                        Based on your review patterns and team dynamics, consider:
                      </Typography>
                      <Box component="ul" sx={{ pl: 2 }}>
                        <li>Providing more specific examples in your comments (increases insight accuracy by 23%)</li>
                        <li>Reviewing teammates across different projects for broader perspective</li>
                        <li>Following up on previous feedback to track improvement trends</li>
                      </Box>
                    </Paper>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Success Snackbar */}
      <Snackbar
        open={showSuccess}
        autoHideDuration={6000}
        onClose={() => setShowSuccess(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={() => setShowSuccess(false)} severity="success" sx={{ width: '100%' }}>
          🎉 Review submitted successfully! AI insights will be updated within 24 hours.
        </Alert>
      </Snackbar>
    </Box>
  );
}
