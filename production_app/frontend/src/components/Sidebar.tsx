import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Box,
  Typography,
  Divider,
  Avatar,
  Chip,
} from '@mui/material';
import {
  Dashboard,
  RateReview,
  Analytics,
  Groups,
  Person,
  AdminPanelSettings,
  Insights,
  TrendingUp,
  Psychology,
  Business,
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const drawerWidth = 280;

interface NavItem {
  text: string;
  icon: React.ReactElement;
  path: string;
  roles?: string[];
  badge?: string;
  description?: string;
}

const navItems: NavItem[] = [
  {
    text: 'Dashboard',
    icon: <Dashboard />,
    path: '/dashboard',
    description: 'Overview and key metrics',
  },
  {
    text: 'Submit Reviews',
    icon: <RateReview />,
    path: '/reviews',
    description: 'Rate your colleagues',
  },
  {
    text: 'Analytics',
    icon: <Analytics />,
    path: '/analytics',
    description: 'Performance insights',
    badge: 'AI',
  },
  {
    text: 'Team',
    icon: <Groups />,
    path: '/team',
    roles: ['manager', 'hr', 'admin'],
    description: 'Team management',
  },
  {
    text: 'My Profile',
    icon: <Person />,
    path: '/profile',
    description: 'Personal settings',
  },
  {
    text: 'Admin Panel',
    icon: <AdminPanelSettings />,
    path: '/admin',
    roles: ['admin'],
    description: 'System administration',
    badge: 'Admin',
  },
];

export default function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, hasRole } = useAuth();

  const filteredNavItems = navItems.filter(item => 
    !item.roles || hasRole(item.roles)
  );

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          background: 'linear-gradient(180deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          borderRight: 'none',
        },
      }}
    >
      {/* Header */}
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Avatar
          sx={{
            width: 60,
            height: 60,
            background: 'rgba(255, 255, 255, 0.2)',
            fontSize: '1.5rem',
            mx: 'auto',
            mb: 2,
            backdropFilter: 'blur(10px)',
          }}
        >
          🚀
        </Avatar>
        <Typography variant="h6" sx={{ fontWeight: 700, mb: 0.5 }}>
          PeerPulse
        </Typography>
        <Typography variant="caption" sx={{ opacity: 0.8 }}>
          Enterprise Edition
        </Typography>
      </Box>

      <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.2)', mx: 2 }} />

      {/* Navigation */}
      <List sx={{ px: 2, py: 2 }}>
        {filteredNavItems.map((item) => {
          const isActive = location.pathname === item.path;
          
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 1 }}>
              <ListItemButton
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: 2,
                  py: 1.5,
                  px: 2,
                  backgroundColor: isActive ? 'rgba(255, 255, 255, 0.2)' : 'transparent',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  },
                  transition: 'all 0.2s ease-in-out',
                }}
              >
                <ListItemIcon sx={{ color: 'white', minWidth: 40 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: isActive ? 600 : 400 }}>
                        {item.text}
                      </Typography>
                      {item.badge && (
                        <Chip 
                          label={item.badge}
                          size="small"
                          sx={{ 
                            height: 20,
                            fontSize: '0.75rem',
                            backgroundColor: 'rgba(255, 255, 255, 0.2)',
                            color: 'white',
                          }}
                        />
                      )}
                    </Box>
                  }
                  secondary={
                    <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                      {item.description}
                    </Typography>
                  }
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      {/* Bottom section */}
      <Box sx={{ mt: 'auto', p: 2 }}>
        <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.2)', mb: 2 }} />
        
        {/* AI Status */}
        <Box 
          sx={{ 
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            borderRadius: 2,
            p: 2,
            mb: 2,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <Psychology sx={{ fontSize: 20 }} />
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              AI Status
            </Typography>
          </Box>
          <Typography variant="caption" sx={{ opacity: 0.8 }}>
            🟢 Gemini AI Active
          </Typography>
        </Box>

        {/* Quick Stats */}
        <Box 
          sx={{ 
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            borderRadius: 2,
            p: 2,
          }}
        >
          <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
            Quick Stats
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="caption" sx={{ opacity: 0.8 }}>
              Team Members:
            </Typography>
            <Typography variant="caption" sx={{ fontWeight: 600 }}>
              25
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="caption" sx={{ opacity: 0.8 }}>
              Reviews Today:
            </Typography>
            <Typography variant="caption" sx={{ fontWeight: 600 }}>
              12
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="caption" sx={{ opacity: 0.8 }}>
              AI Insights:
            </Typography>
            <Typography variant="caption" sx={{ fontWeight: 600 }}>
              8
            </Typography>
          </Box>
        </Box>
      </Box>
    </Drawer>
  );
}
