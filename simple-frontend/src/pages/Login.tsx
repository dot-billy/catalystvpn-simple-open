import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  Collapse,
  IconButton,
  CircularProgress,
  useTheme,
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import { useAuth } from '../contexts/AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [errorDetails, setErrorDetails] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showDebugInfo, setShowDebugInfo] = useState(false);
  
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();
  const theme = useTheme();

  // If already authenticated, redirect to dashboard
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setErrorDetails(null);
    
    try {
      await login(email, password);
      // Navigation will be handled by the useEffect above
    } catch (err: any) {
      setError('Login failed');
      
      // Provide more detailed error information
      if (err.response) {
        // Server responded with non-2xx status
        setErrorDetails(`Server responded with status ${err.response.status}: ${JSON.stringify(err.response.data)}`);
      } else if (err.request) {
        // Request was made but no response received
        setErrorDetails(`No response from server. API might be offline or unreachable: ${err.request.responseURL || 'unknown URL'}`);
      } else {
        // Error in setting up request
        setErrorDetails(`Request error: ${err.message}`);
      }
      
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: `url(/images/space-background.jpg)`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        py: 4,
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.6)',
          zIndex: 1,
        }
      }}
    >
      <Container component="main" maxWidth="sm" sx={{ position: 'relative', zIndex: 2 }}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <Paper
            elevation={6}
            sx={{
              padding: 4,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              width: '100%',
              borderRadius: 2,
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
              background: 'rgba(18, 24, 40, 0.85)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          >
            <Box 
              sx={{ 
                mb: 3, 
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
              }}
            >
              {/* Company Logo */}
              <Box 
                sx={{ 
                  p: 2,
                  mb: 2,
                  borderRadius: '50%',
                  backgroundColor: '#2c3b88',
                  boxShadow: '0 4px 18px rgba(38, 132, 255, 0.6)',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                }}
              >
                <RocketLaunchIcon sx={{ fontSize: 40, color: 'white' }} />
              </Box>
              <Typography component="h1" variant="h4" fontWeight="bold" sx={{ mb: 1, color: 'white' }}>
                CatalystVPN
              </Typography>
              <Typography variant="subtitle1" sx={{ color: 'rgba(255, 255, 255, 0.7)' }} gutterBottom>
                Secure, Simple, and Fast
              </Typography>
            </Box>
            
            {error && (
              <Alert 
                severity="error" 
                sx={{ width: '100%', mb: 3 }}
                action={
                  errorDetails ? 
                  <IconButton 
                    color="inherit" 
                    size="small"
                    onClick={() => setShowDebugInfo(!showDebugInfo)}
                  >
                    <InfoIcon fontSize="inherit" />
                  </IconButton> : null
                }
              >
                {error}
                {errorDetails && (
                  <Collapse in={showDebugInfo}>
                    <Box sx={{ mt: 1, whiteSpace: 'pre-wrap', fontSize: '0.8rem' }}>
                      {errorDetails}
                    </Box>
                  </Collapse>
                )}
              </Alert>
            )}
            
            <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="email"
                label="Email Address"
                name="email"
                autoComplete="email"
                autoFocus
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                sx={{ 
                  mb: 2,
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 1.5,
                    color: 'white',
                    '& fieldset': {
                      borderColor: 'rgba(255, 255, 255, 0.3)',
                    },
                    '&:hover fieldset': {
                      borderColor: 'rgba(255, 255, 255, 0.5)',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#5d87ff',
                    }
                  },
                  '& .MuiInputLabel-root': {
                    color: 'rgba(255, 255, 255, 0.7)',
                  },
                  '& .MuiInputLabel-root.Mui-focused': {
                    color: '#5d87ff',
                  }
                }}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type="password"
                id="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                sx={{ 
                  mb: 3,
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 1.5,
                    color: 'white',
                    '& fieldset': {
                      borderColor: 'rgba(255, 255, 255, 0.3)',
                    },
                    '&:hover fieldset': {
                      borderColor: 'rgba(255, 255, 255, 0.5)',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#5d87ff',
                    }
                  },
                  '& .MuiInputLabel-root': {
                    color: 'rgba(255, 255, 255, 0.7)',
                  },
                  '& .MuiInputLabel-root.Mui-focused': {
                    color: '#5d87ff',
                  }
                }}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ 
                  mt: 1, 
                  mb: 3,
                  py: 1.5,
                  borderRadius: 1.5,
                  textTransform: 'none',
                  fontSize: '1.1rem',
                  background: 'linear-gradient(90deg, #2c3b88 0%, #5d87ff 100%)',
                  boxShadow: '0 4px 15px rgba(93, 135, 255, 0.3)',
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    background: 'linear-gradient(90deg, #2c3b88 0%, #5d87ff 70%)',
                    boxShadow: '0 6px 20px rgba(93, 135, 255, 0.4)',
                    transform: 'translateY(-2px)'
                  }
                }}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <CircularProgress size={24} sx={{ mr: 1 }} />
                    Launching...
                  </>
                ) : 'Launch Secure Connection'}
              </Button>
              
              <Typography variant="body2" align="center" sx={{ mt: 2, color: 'rgba(255, 255, 255, 0.5)' }}>
                © {new Date().getFullYear()} CatalystVPN
              </Typography>
            </Box>
          </Paper>
        </Box>
      </Container>
    </Box>
  );
} 