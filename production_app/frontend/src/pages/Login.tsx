import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Container,
  Avatar,
  Divider,
  Chip,
} from '@mui/material';
import { RocketLaunch, Business, Psychology, Groups } from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const success = await login(email, password);
      if (!success) {
        setError('Invalid email or password');
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const demoLogins = [
    { role: 'Employee', email: 'jamie.brown@company.com', icon: <Business /> },
    { role: 'Manager', email: 'manager@company.com', icon: <Groups /> },
    { role: 'HR', email: 'hr@company.com', icon: <Psychology /> },
    { role: 'Admin', email: 'admin@company.com', icon: <RocketLaunch /> },
  ];

  const handleDemoLogin = (demoEmail: string) => {
    setEmail(demoEmail);
    setPassword('demo123');
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2,
      }}
    >
      <Container maxWidth="md">
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Avatar
            sx={{
              width: 80,
              height: 80,
              background: 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)',
              fontSize: '2rem',
              mx: 'auto',
              mb: 2,
            }}
          >
            🚀
          </Avatar>
          <Typography variant="h3" component="h1" sx={{ color: 'white', fontWeight: 700, mb: 1 }}>
            PeerPulse Enterprise
          </Typography>
          <Typography variant="h6" sx={{ color: 'rgba(255,255,255,0.9)', mb: 3 }}>
            AI-Powered Performance Management System
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', gap: 3, alignItems: 'flex-start' }}>
          {/* Login Form */}
          <Card sx={{ flexGrow: 1, maxWidth: 400 }}>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h5" component="h2" gutterBottom sx={{ textAlign: 'center', mb: 3 }}>
                Welcome Back
              </Typography>

              <form onSubmit={handleSubmit}>
                <TextField
                  fullWidth
                  label="Email Address"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  margin="normal"
                  required
                  autoFocus
                  sx={{ mb: 2 }}
                />

                <TextField
                  fullWidth
                  label="Password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  margin="normal"
                  required
                  sx={{ mb: 3 }}
                />

                {error && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                  </Alert>
                )}

                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={isLoading}
                  sx={{
                    py: 1.5,
                    background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                    boxShadow: '0 3px 5px 2px rgba(102, 126, 234, .3)',
                  }}
                >
                  {isLoading ? <CircularProgress size={24} color="inherit" /> : 'Sign In'}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Demo Accounts */}
          <Card sx={{ minWidth: 320 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ textAlign: 'center', mb: 2 }}>
                🎮 Try Demo Accounts
              </Typography>
              
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3, textAlign: 'center' }}>
                Click any role below to instantly log in and explore the system
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                {demoLogins.map((demo) => (
                  <Button
                    key={demo.role}
                    variant="outlined"
                    startIcon={demo.icon}
                    onClick={() => handleDemoLogin(demo.email)}
                    sx={{
                      justifyContent: 'flex-start',
                      textAlign: 'left',
                      p: 1.5,
                      '&:hover': {
                        background: 'linear-gradient(45deg, rgba(102, 126, 234, 0.1) 30%, rgba(118, 75, 162, 0.1) 90%)',
                      },
                    }}
                  >
                    <Box>
                      <Typography variant="subtitle2" component="div">
                        {demo.role}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {demo.email}
                      </Typography>
                    </Box>
                  </Button>
                ))}
              </Box>

              <Divider sx={{ my: 2 }} />

              <Typography variant="caption" color="text.secondary" sx={{ textAlign: 'center', display: 'block' }}>
                🔐 Any password works for demo accounts
              </Typography>
            </CardContent>
          </Card>
        </Box>

        {/* Features */}
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
            <Chip label="🧠 AI-Powered Insights" sx={{ color: 'white', borderColor: 'white' }} variant="outlined" />
            <Chip label="📊 Real-time Analytics" sx={{ color: 'white', borderColor: 'white' }} variant="outlined" />
            <Chip label="🔒 Enterprise Security" sx={{ color: 'white', borderColor: 'white' }} variant="outlined" />
            <Chip label="📱 Mobile Ready" sx={{ color: 'white', borderColor: 'white' }} variant="outlined" />
          </Box>
        </Box>
      </Container>
    </Box>
  );
}
