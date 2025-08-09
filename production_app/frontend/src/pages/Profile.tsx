import React from 'react';
import { Box, Typography, Card, CardContent, Chip } from '@mui/material';

export default function Profile() {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
        My Profile
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Manage your personal settings and preferences
      </Typography>
      
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 6 }}>
          <Typography variant="h6" gutterBottom>
            👤 Profile Settings Coming Soon
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Personal profile management and settings.
          </Typography>
          <Chip label="User Settings" color="info" />
        </CardContent>
      </Card>
    </Box>
  );
}
