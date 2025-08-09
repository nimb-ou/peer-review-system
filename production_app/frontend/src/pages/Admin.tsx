import React from 'react';
import { Box, Typography, Card, CardContent, Chip } from '@mui/material';

export default function Admin() {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
        Admin Panel
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        System administration and configuration
      </Typography>
      
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 6 }}>
          <Typography variant="h6" gutterBottom>
            👑 Admin Features Coming Soon
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Administrative controls and system management.
          </Typography>
          <Chip label="Admin Only" color="error" />
        </CardContent>
      </Card>
    </Box>
  );
}
