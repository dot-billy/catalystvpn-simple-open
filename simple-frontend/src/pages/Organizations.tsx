import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Avatar,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Tooltip,
  Chip,
  Alert,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import Grid from '../components/CustomGrid';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Business as BusinessIcon,
  Hub as HubIcon,
  Lightbulb as LightbulbIcon,
  Security as SecurityIcon,
  VpnKey as VpnKeyIcon,
  ArrowForward as ArrowForwardIcon,
  Computer as ComputerIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { organizations } from '../services/api';

interface OrganizationFormData {
  name: string;
  description: string;
  password?: string;
}

interface Organization {
  id: string;
  name: string;
  description?: string;
  nodes_count?: number;
  lighthouses_count?: number;
  security_groups_count?: number;
  certificates_count?: number;
  networks_count?: number;
  slug?: string;
  created_at?: string;
  updated_at?: string;
  status?: string;
}

const Organizations: React.FC = () => {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [editOrg, setEditOrg] = useState<Organization | null>(null);
  const [formData, setFormData] = useState<OrganizationFormData>({
    name: '',
    description: '',
  });
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  // Fetch organizations
  const { data: orgsList, isLoading, error: fetchError } = useQuery({
    queryKey: ['organizations'],
    queryFn: async () => {
      console.log('Fetching organizations with include_counts=true');
      const response = await organizations.list();
      console.log('Organizations response:', response);
      return response.data;
    },
  });

  // Create organization mutation
  const createMutation = useMutation({
    mutationFn: (newOrg: any) => organizations.create(newOrg),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
      handleClose();
    },
    onError: (error: any) => {
      setError(error.message || 'Failed to create organization');
    },
  });

  // Update organization mutation
  const updateMutation = useMutation({
    mutationFn: (updatedOrg: any) => organizations.update(updatedOrg.id, updatedOrg),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
      handleClose();
    },
    onError: (error: any) => {
      setError(error.message || 'Failed to update organization');
    },
  });

  // Delete organization mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => organizations.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
    },
    onError: (error: any) => {
      setError(error.message || 'Failed to delete organization');
    },
  });

  const handleClickOpen = () => {
    setOpen(true);
    setEditOrg(null);
    setFormData({
      name: '',
      description: '',
    });
    setError(null);
  };

  const handleEdit = (org: any) => {
    setEditOrg(org);
    setFormData({
      name: org.name,
      description: org.description || '',
    });
    setOpen(true);
    setError(null);
  };

  const handleClose = () => {
    setOpen(false);
    setEditOrg(null);
    setFormData({
      name: '',
      description: '',
    });
    setError(null);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editOrg) {
      const updatedOrg: OrganizationFormData = {
        ...formData,
      };
      updateMutation.mutate({
        id: editOrg.id,
        ...updatedOrg,
      });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this organization?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleViewDetails = (id: string) => {
    navigate(`/organizations/${id}`);
  };

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Organizations
        </Typography>
        <Typography>Loading organizations...</Typography>
      </Box>
    );
  }

  if (fetchError) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Organizations
        </Typography>
        <Alert severity="error">
          Error loading organizations: {(fetchError as Error).message}
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Organizations
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleClickOpen}
        >
          Add Organization
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {isLoading ? (
        <Typography>Loading organizations...</Typography>
      ) : (
        <Paper sx={{ width: '100%', overflow: 'hidden' }}>
          <TableContainer sx={{ maxHeight: 600 }}>
            <Table stickyHeader aria-label="organizations table">
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {orgsList?.map((org: any) => (
                  <TableRow 
                    key={org.id}
                    hover
                    onClick={() => handleViewDetails(org.id)}
                    sx={{ 
                      cursor: 'pointer',
                      '&:last-child td, &:last-child th': { border: 0 } 
                    }}
                  >
                    <TableCell>
                      <Typography variant="body1" fontWeight="500">
                        {org.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {org.slug || org.id.substring(0, 8)}
                      </Typography>
                    </TableCell>
                    <TableCell sx={{ maxWidth: 300 }}>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          overflow: 'hidden', 
                          textOverflow: 'ellipsis',
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical'
                        }}
                      >
                        {org.description || 'No description provided'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {new Date(org.created_at || Date.now()).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Chip 
                        size="small" 
                        label={org.status === 'inactive' ? 'Inactive' : 'Active'}
                        color={org.status === 'inactive' ? 'error' : 'success'}
                      />
                    </TableCell>
                    <TableCell align="right" onClick={(e) => e.stopPropagation()}>
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleViewDetails(org.id);
                          }}
                        >
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit Organization">
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEdit(org);
                          }}
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete Organization">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDelete(org.id);
                          }}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
                {!orgsList || orgsList.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      <Typography variant="body1" py={4}>
                        No organizations found. Create your first organization.
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : null}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editOrg ? 'Edit Organization' : 'Add New Organization'}
        </DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              name="name"
              label="Organization Name"
              type="text"
              fullWidth
              variant="outlined"
              value={formData.name}
              onChange={handleChange}
              required
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              name="description"
              label="Description"
              type="text"
              fullWidth
              variant="outlined"
              value={formData.description}
              onChange={handleChange}
              multiline
              rows={4}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button
              type="submit"
              variant="contained"
              disabled={createMutation.isPending || updateMutation.isPending}
            >
              {editOrg ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

export default Organizations; 