import React from 'react';
import { Box, Typography, Card, CardContent, Chip } from '@mui/material';

export default function Team() {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
        Team Management
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Manage your team members and view team analytics
      </Typography>
      
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 6 }}>
          <Typography variant="h6" gutterBottom>
            👥 Team Dashboard Coming Soon
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Team management features for managers and administrators.
          </Typography>
          <Chip label="Manager Access Required" color="warning" />
        </CardContent>
      </Card>
    </Box>
  );
}
