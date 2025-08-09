import React from 'react';
import { Box, Typography, Card, CardContent, Grid, Chip } from '@mui/material';

export default function Analytics() {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
        Analytics
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Advanced performance analytics and AI insights
      </Typography>
      
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 6 }}>
          <Typography variant="h6" gutterBottom>
            🚧 Analytics Dashboard Coming Soon
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Advanced analytics with team performance metrics, trend analysis, and predictive insights.
          </Typography>
          <Chip label="🧠 Powered by Gemini AI" color="primary" />
        </CardContent>
      </Card>
    </Box>
  );
}
