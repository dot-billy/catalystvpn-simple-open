import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Tooltip,
  Alert,
  Paper,
  Chip,
  Snackbar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  FormControl,
  FormControlLabel,
  Checkbox,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Shield as ShieldIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

// Mock data - replace with actual API calls when available
const MOCK_ROLES = [
  {
    id: '1',
    name: 'Administrator',
    description: 'Full system access',
    permissions: ['users:read', 'users:write', 'security:read', 'security:write', 'nodes:read', 'nodes:write'],
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  },
  {
    id: '2',
    name: 'Operator',
    description: 'Can manage nodes and security groups',
    permissions: ['users:read', 'security:read', 'security:write', 'nodes:read', 'nodes:write'],
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  },
  {
    id: '3',
    name: 'User',
    description: 'Standard user access',
    permissions: ['security:read', 'nodes:read'],
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  },
  {
    id: '4',
    name: 'Auditor',
    description: 'Read-only access for auditing purposes',
    permissions: ['users:read', 'security:read', 'nodes:read'],
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  },
  {
    id: '5',
    name: 'Guest',
    description: 'Limited view access',
    permissions: ['nodes:read'],
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  }
];

// Available permissions in the system
const AVAILABLE_PERMISSIONS = [
  { id: 'users:read', name: 'View Users' },
  { id: 'users:write', name: 'Manage Users' },
  { id: 'security:read', name: 'View Security Groups' },
  { id: 'security:write', name: 'Manage Security Groups' },
  { id: 'nodes:read', name: 'View Nodes' },
  { id: 'nodes:write', name: 'Manage Nodes' }
];

interface Role {
  id: string;
  name: string;
  description: string;
  permissions: string[];
  created_at: string;
  updated_at: string;
}

interface FormData {
  name: string;
  description: string;
  permissions: string[];
}

const Roles: React.FC = () => {
  const [roles, setRoles] = useState<Role[]>(MOCK_ROLES);
  const [open, setOpen] = useState(false);
  const [editRole, setEditRole] = useState<Role | null>(null);
  const [formData, setFormData] = useState<FormData>({
    name: '',
    description: '',
    permissions: []
  });
  const [error, setError] = useState<string | null>(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const { user } = useAuth();

  // Check if current user has admin role (for demonstration - use proper auth system in production)
  const hasPermission = () => {
    // For now, assume 'is_admin' property exists on user object
    return (user as any)?.is_admin === true;
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleClickOpen = () => {
    setOpen(true);
    setEditRole(null);
    setFormData({
      name: '',
      description: '',
      permissions: []
    });
    setError(null);
  };

  const handleEdit = (role: Role) => {
    setEditRole(role);
    setFormData({
      name: role.name || '',
      description: role.description || '',
      permissions: [...(role.permissions || [])]
    });
    setOpen(true);
    setError(null);
  };

  const handleClose = () => {
    setOpen(false);
    setEditRole(null);
    setFormData({
      name: '',
      description: '',
      permissions: []
    });
    setError(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      // Validation
      if (!formData.name) {
        setError('Role name is required');
        return;
      }
      
      if (editRole) {
        // Update existing role
        const updatedRoles = roles.map(role => 
          role.id === editRole.id 
            ? { 
                ...role, 
                name: formData.name, 
                description: formData.description, 
                permissions: formData.permissions,
                updated_at: new Date().toISOString()
              } 
            : role
        );
        setRoles(updatedRoles);
        setSnackbar({
          open: true,
          message: 'Role updated successfully',
          severity: 'success'
        });
      } else {
        // Create new role
        const newRole: Role = {
          id: Math.random().toString(36).substring(2, 9), // Simple ID generation
          name: formData.name,
          description: formData.description,
          permissions: formData.permissions,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        setRoles([...roles, newRole]);
        setSnackbar({
          open: true,
          message: 'Role created successfully',
          severity: 'success'
        });
      }
      
      handleClose();
    } catch (error) {
      setError('An error occurred. Please try again.');
      setSnackbar({
        open: true,
        message: 'Error: Failed to save role',
        severity: 'error'
      });
    }
  };

  const handleDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this role?')) {
      try {
        const updatedRoles = roles.filter(role => role.id !== id);
        setRoles(updatedRoles);
        setSnackbar({
          open: true,
          message: 'Role deleted successfully',
          severity: 'success'
        });
      } catch (error) {
        setSnackbar({
          open: true,
          message: 'Error: Failed to delete role',
          severity: 'error'
        });
      }
    }
  };

  const handlePermissionChange = (permission: string) => {
    setFormData(prev => {
      const updatedPermissions = prev.permissions.includes(permission)
        ? prev.permissions.filter(p => p !== permission)
        : [...prev.permissions, permission];
        
      return {
        ...prev,
        permissions: updatedPermissions
      };
    });
  };

  const formatDate = (dateString: string): string => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  // Get displayed roles based on pagination
  const displayedRoles = roles.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Role Management
        </Typography>
        {hasPermission() && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleClickOpen}
          >
            Add Role
          </Button>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {!hasPermission() && (
        <Alert severity="info" sx={{ mb: 3 }}>
          You need administrator privileges to manage roles. Contact your system administrator.
        </Alert>
      )}

      <Paper sx={{ width: '100%', mb: 2 }}>
        <TableContainer sx={{ maxHeight: 440 }}>
          <Table stickyHeader aria-label="roles table">
            <TableHead>
              <TableRow>
                <TableCell>Role Name</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Permissions</TableCell>
                <TableCell>Last Updated</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {displayedRoles.map((role) => (
                <TableRow key={role.id} hover>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <ShieldIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="body2">{role.name}</Typography>
                    </Box>
                  </TableCell>
                  <TableCell>{role.description}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {(role.permissions || []).map((permission) => (
                        <Chip 
                          key={permission}
                          size="small"
                          label={AVAILABLE_PERMISSIONS.find(p => p.id === permission)?.name || permission}
                          color="primary"
                          variant="outlined"
                          icon={<SecurityIcon />}
                        />
                      ))}
                    </Box>
                  </TableCell>
                  <TableCell>{formatDate(role.updated_at || role.created_at)}</TableCell>
                  <TableCell>
                    <Tooltip title="Edit Role">
                      <IconButton
                        color="primary"
                        onClick={() => handleEdit(role)}
                        size="small"
                        disabled={!hasPermission()}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete Role">
                      <IconButton
                        color="error"
                        onClick={() => handleDelete(role.id)}
                        size="small"
                        disabled={!hasPermission()}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={roles.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>

      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>
          {editRole ? 'Edit Role' : 'Add Role'}
        </DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Role Name"
              type="text"
              fullWidth
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Description"
              type="text"
              fullWidth
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              sx={{ mb: 3 }}
            />
            
            <Typography variant="subtitle1" gutterBottom>
              Permissions
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, ml: 2 }}>
              {AVAILABLE_PERMISSIONS.map((permission) => (
                <FormControlLabel
                  key={permission.id}
                  control={
                    <Checkbox
                      checked={formData.permissions.includes(permission.id)}
                      onChange={() => handlePermissionChange(permission.id)}
                    />
                  }
                  label={permission.name}
                />
              ))}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button
              type="submit"
              variant="contained"
            >
              {editRole ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
      
      <Snackbar 
        open={snackbar.open} 
        autoHideDuration={6000} 
        onClose={() => setSnackbar({...snackbar, open: false})}
      >
        <Alert 
          onClose={() => setSnackbar({...snackbar, open: false})} 
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Roles; 