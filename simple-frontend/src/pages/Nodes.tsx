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
  Divider,
} from '@mui/material';
import Grid from '../components/CustomGrid';
import { 
  Add as AddIcon, 
  Edit as EditIcon, 
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { organizations, nodes } from '../services/api';
import { Node } from '../types';

const Nodes: React.FC = () => {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
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

  // Get nodes for the first organization
  const { data, isLoading, error } = useQuery<Node[]>({
    queryKey: ['nodes', orgId],
    queryFn: async () => {
      if (!orgId) return [];
      const response = await nodes.list(orgId);
      return response.data;
    },
    enabled: !!orgId,
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => nodes.create(orgId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nodes', orgId] });
      setOpen(false);
      setFormData({ name: '', ip_address: '', description: '' });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => nodes.delete(orgId!, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nodes', orgId] });
    },
  });

  const checkInMutation = useMutation({
    mutationFn: (id: string) => nodes.checkIn(orgId!, id, {}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nodes', orgId] });
    },
  });

  const generateConfigMutation = useMutation({
    mutationFn: (id: string) => nodes.generateConfig(orgId!, id),
    onSuccess: (response) => {
      // Create a blob and download the config
      const blob = new Blob([response.data], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `node-config-${selectedNode?.name || 'unknown'}.txt`;
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

  if (!orgId) {
    return (
      <Box p={3}>
        <Alert severity="info">
          No organizations found. Please create an organization first.
        </Alert>
      </Box>
    );
  }

  if (isLoading) {
    return (
      <Box p={3}>
        <Typography variant="h4" gutterBottom>
          Nodes
        </Typography>
        <Skeleton variant="rectangular" width="100%" height={400} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Error loading nodes: {error.message}
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Nodes</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleOpen}
        >
          Add Node
        </Button>
      </Box>

      <Grid container spacing={3}>
        {data?.map((node) => (
          <Grid item xs={12} sm={6} md={4} key={node.id}>
            <Paper>
              <Box display="flex" justifyContent="space-between" alignItems="center" p={2}>
                <Typography variant="h6">{node.name}</Typography>
                <Chip 
                  label={node.status} 
                  color={getStatusColor(node.status) as any} 
                  size="small" 
                />
              </Box>
              <Divider />
              <Box p={2}>
                <Typography variant="body2" color="text.secondary">
                  IP Address
                </Typography>
                <Typography variant="body1">
                  {node.ip_address}
                </Typography>
              </Box>
              <Box p={2}>
                <Typography variant="body2" color="text.secondary">
                  ID
                </Typography>
                <Typography variant="body1" sx={{ wordBreak: 'break-all' }}>
                  {node.id}
                </Typography>
              </Box>
              <Box p={2} display="flex" justifyContent="flex-end">
                <Tooltip title="Check In">
                  <IconButton 
                    size="small" 
                    onClick={() => {
                      setSelectedNode(node);
                      checkInMutation.mutate(node.id);
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
                      setSelectedNode(node);
                      generateConfigMutation.mutate(node.id);
                    }}
                    disabled={generateConfigMutation.isPending}
                  >
                    <DownloadIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Edit">
                  <IconButton 
                    size="small" 
                    onClick={() => {
                      // TODO: Implement edit node
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
                      if (window.confirm('Are you sure you want to delete this node?')) {
                        deleteMutation.mutate(node.id);
                      }
                    }}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>

      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Add Node</DialogTitle>
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

export default Nodes; 