import React, { useState } from 'react';
import {
  Box,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  IconButton,
  Skeleton,
  Alert,
  Chip,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Card,
  CardContent,
  CardActions,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  LinearProgress,
  Avatar,
} from '@mui/material';
import Grid from '../components/CustomGrid';
import { 
  Add as AddIcon, 
  Edit as EditIcon, 
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Info as InfoIcon,
  Hub as HubIcon
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { organizations, lighthouses } from '../services/api';
import { Lighthouse } from '../types';

const Lighthouses: React.FC = () => {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [selectedLighthouse, setSelectedLighthouse] = useState<Lighthouse | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    ip_address: '',
    description: '',
  });

  // First get the organizations
  const { data: orgs, isLoading: orgsLoading, error: orgsError } = useQuery({
    queryKey: ['organizations'],
    queryFn: async () => {
      const response = await organizations.list();
      return response.data;
    },
  });

  // Get the first organization's ID to use for nested endpoints
  const orgId = orgs?.[0]?.id;

  // Get lighthouses for the first organization
  const { data, isLoading, error } = useQuery<Lighthouse[]>({
    queryKey: ['lighthouses'],
    queryFn: async () => {
      const response = await lighthouses.list();
      return response.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => lighthouses.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lighthouses'] });
      setOpen(false);
      setFormData({ name: '', ip_address: '', description: '' });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => lighthouses.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lighthouses'] });
    },
  });

  const checkInMutation = useMutation({
    mutationFn: (id: string) => lighthouses.checkIn(id, {}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lighthouses'] });
    },
  });

  const generateConfigMutation = useMutation({
    mutationFn: (id: string) => lighthouses.generateConfig(id),
    onSuccess: (response) => {
      // Create a blob and download the config
      const blob = new Blob([response.data], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `lighthouse-config-${selectedLighthouse?.name || 'unknown'}.txt`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    },
  });

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const getStatusColor = (status: string | undefined) => {
    if (!status) return 'default';
    
    switch (status.toLowerCase()) {
      case 'online':
        return 'success';
      case 'offline':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  if (orgsLoading) {
    return (
      <Box p={3}>
        <Skeleton variant="text" width={200} height={40} />
        <Skeleton variant="rectangular" width="100%" height={400} />
      </Box>
    );
  }

  if (orgsError) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Error loading organizations: {orgsError.message}
        </Alert>
      </Box>
    );
  }

  if (isLoading) {
    return (
      <Box p={3}>
        <Typography variant="h4" gutterBottom>
          Lighthouses
        </Typography>
        <Skeleton variant="rectangular" width="100%" height={400} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Error loading lighthouses: {error.message}
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Lighthouses</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleOpen}
        >
          Add Lighthouse
        </Button>
      </Box>

      <Grid container spacing={3}>
        {data?.map((lighthouse) => (
          <Grid item xs={12} sm={6} md={4} key={lighthouse.id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6">{lighthouse.name}</Typography>
                  <Chip 
                    label={lighthouse.status} 
                    color={getStatusColor(lighthouse.status) as any} 
                    size="small" 
                  />
                </Box>
                <Divider sx={{ my: 1.5 }} />
                <Box mb={1}>
                  <Typography variant="body2" color="text.secondary">
                    IP Address
                  </Typography>
                  <Typography variant="body1">
                    {lighthouse.ip_address}
                  </Typography>
                </Box>
                <Box mb={1}>
                  <Typography variant="body2" color="text.secondary">
                    ID
                  </Typography>
                  <Typography variant="body1" sx={{ wordBreak: 'break-all' }}>
                    {lighthouse.id}
                  </Typography>
                </Box>
              </CardContent>
              <CardActions>
                <Tooltip title="Check In">
                  <IconButton 
                    size="small" 
                    onClick={() => {
                      setSelectedLighthouse(lighthouse);
                      checkInMutation.mutate(lighthouse.id);
                    }}
                    disabled={checkInMutation.isPending}
                  >
                    <RefreshIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Generate Config">
                  <IconButton 
                    size="small" 
                    onClick={() => {
                      setSelectedLighthouse(lighthouse);
                      generateConfigMutation.mutate(lighthouse.id);
                    }}
                    disabled={generateConfigMutation.isPending}
                  >
                    <DownloadIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="View Connected Nodes">
                  <IconButton 
                    size="small" 
                    onClick={() => {
                      // TODO: Implement view connected nodes
                    }}
                  >
                    <HubIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Edit">
                  <IconButton 
                    size="small" 
                    onClick={() => {
                      // TODO: Implement edit lighthouse
                    }}
                  >
                    <EditIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Delete">
                  <IconButton 
                    size="small" 
                    color="error"
                    onClick={() => {
                      if (window.confirm('Are you sure you want to delete this lighthouse?')) {
                        deleteMutation.mutate(lighthouse.id);
                      }
                    }}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Add Lighthouse</DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              name="name"
              label="Name"
              type="text"
              fullWidth
              variant="outlined"
              value={formData.name}
              onChange={handleChange}
              required
            />
            <TextField
              margin="dense"
              name="ip_address"
              label="IP Address"
              type="text"
              fullWidth
              variant="outlined"
              value={formData.ip_address}
              onChange={handleChange}
              required
            />
            <TextField
              margin="dense"
              name="description"
              label="Description"
              type="text"
              fullWidth
              variant="outlined"
              multiline
              rows={3}
              value={formData.description}
              onChange={handleChange}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button type="submit" variant="contained" color="primary" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

export default Lighthouses; 