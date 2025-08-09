import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Avatar,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider,
  Paper,
  IconButton,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  Psychology,
  Groups,
  Star,
  Warning,
  CheckCircle,
  ArrowForward,
  Insights,
  EmojiEvents,
  Speed,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

// Mock data
const performanceData = [
  { name: 'Jan', score: 3.2 },
  { name: 'Feb', score: 3.5 },
  { name: 'Mar', score: 3.8 },
  { name: 'Apr', score: 4.1 },
  { name: 'May', score: 4.2 },
  { name: 'Jun', score: 4.0 },
];

const teamData = [
  { name: 'Collaborative', value: 65, color: '#4caf50' },
  { name: 'Neutral', value: 25, color: '#ff9800' },
  { name: 'Withdrawn', value: 8, color: '#f44336' },
  { name: 'Blocking', value: 2, color: '#9c27b0' },
];

const recentInsights = [
  {
    id: 1,
    employee: 'Jamie Brown',
    type: 'positive',
    insight: 'Showing exceptional collaboration skills and leadership potential',
    confidence: 92,
    avatar: 'JB',
  },
  {
    id: 2,
    employee: 'Quinn Davis',
    type: 'warning',
    insight: 'May benefit from additional support and mentoring',
    confidence: 87,
    avatar: 'QD',
  },
  {
    id: 3,
    employee: 'River Anderson',
    type: 'neutral',
    insight: 'Steady performance with room for growth in team collaboration',
    confidence: 79,
    avatar: 'RA',
  },
];

const upcomingTasks = [
  { id: 1, title: 'Submit Q2 peer reviews', due: 'Due in 3 days', priority: 'high' },
  { id: 2, title: 'Team sync meeting', due: 'Tomorrow 2 PM', priority: 'medium' },
  { id: 3, title: 'Performance goal check-in', due: 'Next week', priority: 'low' },
];

export default function Dashboard() {
  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Get insights into team performance and collaboration patterns
        </Typography>
      </Box>

      {/* Quick Actions Alert */}
      <Alert 
        severity="info" 
        sx={{ mb: 3, borderRadius: 2 }}
        action={
          <Button color="inherit" size="small">
            Review Now
          </Button>
        }
      >
        🎯 You have 3 pending peer reviews to submit. Stay on track with your quarterly goals!
      </Alert>

      <Grid container spacing={3}>
        {/* KPI Cards */}
        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">Your Score</Typography>
                <TrendingUp />
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
                4.2
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                +0.3 from last month
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={84} 
                sx={{ mt: 2, backgroundColor: 'rgba(255,255,255,0.2)' }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">AI Insights</Typography>
                <Psychology color="primary" />
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
                8
              </Typography>
              <Typography variant="body2" color="text.secondary">
                New insights this week
              </Typography>
              <Chip label="🔥 Hot" size="small" color="error" sx={{ mt: 1 }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">Team Health</Typography>
                <Groups color="primary" />
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
                87%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Collaboration index
              </Typography>
              <Chip label="📈 Improving" size="small" color="success" sx={{ mt: 1 }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">Reviews</Typography>
                <Star color="primary" />
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
                15
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Completed this month
              </Typography>
              <Chip label="✅ On track" size="small" color="success" sx={{ mt: 1 }} />
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Trend */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">Performance Trend</Typography>
                <Button size="small" endIcon={<ArrowForward />}>
                  View Details
                </Button>
              </Box>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis domain={[0, 5]} />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="score" 
                    stroke="#667eea" 
                    strokeWidth={3}
                    dot={{ fill: '#667eea', strokeWidth: 2, r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Team Collaboration */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Team Collaboration
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={teamData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    dataKey="value"
                  >
                    {teamData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <Box sx={{ mt: 2 }}>
                {teamData.map((item) => (
                  <Box key={item.name} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ width: 12, height: 12, backgroundColor: item.color, borderRadius: '50%' }} />
                      <Typography variant="body2">{item.name}</Typography>
                    </Box>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {item.value}%
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* AI Insights */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                  🧠 AI-Powered Insights
                </Typography>
                <Button size="small" endIcon={<ArrowForward />}>
                  View All
                </Button>
              </Box>
              <List>
                {recentInsights.map((insight, index) => (
                  <React.Fragment key={insight.id}>
                    <ListItem alignItems="flex-start" sx={{ px: 0 }}>
                      <ListItemAvatar>
                        <Avatar sx={{ 
                          background: insight.type === 'positive' ? '#4caf50' : 
                                     insight.type === 'warning' ? '#ff9800' : '#2196f3' 
                        }}>
                          {insight.avatar}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                              {insight.employee}
                            </Typography>
                            <Chip 
                              size="small" 
                              label={`${insight.confidence}% confidence`}
                              color={insight.type === 'positive' ? 'success' : insight.type === 'warning' ? 'warning' : 'info'}
                              variant="outlined"
                            />
                          </Box>
                        }
                        secondary={
                          <Typography variant="body2" color="text.secondary">
                            {insight.insight}
                          </Typography>
                        }
                      />
                      <IconButton size="small">
                        {insight.type === 'positive' ? <CheckCircle color="success" /> : 
                         insight.type === 'warning' ? <Warning color="warning" /> : 
                         <Insights color="info" />}
                      </IconButton>
                    </ListItem>
                    {index < recentInsights.length - 1 && <Divider variant="inset" component="li" />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Upcoming Tasks */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📋 Upcoming Tasks
              </Typography>
              <List sx={{ py: 0 }}>
                {upcomingTasks.map((task, index) => (
                  <React.Fragment key={task.id}>
                    <ListItem sx={{ px: 0, py: 1 }}>
                      <ListItemText
                        primary={
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {task.title}
                          </Typography>
                        }
                        secondary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                            <Typography variant="caption" color="text.secondary">
                              {task.due}
                            </Typography>
                            <Chip 
                              size="small" 
                              label={task.priority}
                              color={task.priority === 'high' ? 'error' : task.priority === 'medium' ? 'warning' : 'default'}
                              variant="outlined"
                            />
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < upcomingTasks.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
              <Button fullWidth variant="outlined" sx={{ mt: 2 }}>
                View All Tasks
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)' }}>
            <Typography variant="h6" gutterBottom>
              🚀 Quick Actions
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Button 
                  fullWidth 
                  variant="contained" 
                  startIcon={<Star />}
                  sx={{ py: 1.5 }}
                >
                  Submit Review
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button 
                  fullWidth 
                  variant="outlined" 
                  startIcon={<Psychology />}
                  sx={{ py: 1.5 }}
                >
                  View AI Insights
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button 
                  fullWidth 
                  variant="outlined" 
                  startIcon={<Groups />}
                  sx={{ py: 1.5 }}
                >
                  Team Overview
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button 
                  fullWidth 
                  variant="outlined" 
                  startIcon={<Speed />}
                  sx={{ py: 1.5 }}
                >
                  Performance Goals
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
