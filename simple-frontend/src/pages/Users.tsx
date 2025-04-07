import React, { useState, useEffect } from 'react';
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
  FormControlLabel,
  Switch,
  Snackbar,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Person as PersonIcon,
  AdminPanelSettings as AdminIcon,
  Security as SecurityIcon,
  Verified as VerifiedIcon,
  Block as BlockIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { users, organizations } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface User {
  id: string;
  name: string;
  email: string;
  password?: string;
  is_admin: boolean;
  organizations?: OrganizationRole[];
  status: string;
  created_at?: string;
  last_login?: string;
}

interface OrganizationRole {
  organization_id: string;
  organization_name: string;
  role: string;
}

interface Organization {
  id: string;
  name: string;
  slug: string;
}

interface Member {
  id: string;
  user: {
    id: number;
    email: string;
    full_name: string;
    is_active: boolean;
    date_joined: string;
  };
  organization: string;
  role: string;
  created_at: string;
  updated_at: string;
}

interface AuthUser {
  email: string;
  name: string;
  is_admin?: boolean;
}

interface FormData {
  name: string;
  email: string;
  password: string;
  is_admin: boolean;
  role: string;
  status: string;
  organizationMemberships: OrganizationMembership[];
}

interface OrganizationMembership {
  organization_id: string;
  organization_name: string;
  role: string;
}

interface Window {
  authUser?: any;
}

const Users: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [editUser, setEditUser] = useState<User | null>(null);
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    password: '',
    is_admin: false,
    role: 'user',
    status: 'active',
    organizationMemberships: []
  });
  const [error, setError] = useState<string | null>(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [selectedOrg, setSelectedOrg] = useState<string>('all');
  const queryClient = useQueryClient();
  const { user } = useAuth();

  // Fetch organizations that the current user belongs to
  const { data: organizationsList, isLoading: orgsLoading } = useQuery({
    queryKey: ['organizations'],
    queryFn: async () => {
      const response = await organizations.list();
      return response.data;
    },
  });

  // Fetch user and membership data for each organization
  const { data: memberships, isLoading: membershipsLoading } = useQuery({
    queryKey: ['memberships'],
    queryFn: async () => {
      // First get all orgs user is a member of
      const orgsResponse = await organizations.list();
      
      // For each org, get all members
      const membershipsByOrg: Record<string, Member[]> = {};
      
      await Promise.all(orgsResponse.data.map(async (org: any) => {
        try {
          const membersResponse = await organizations.members.list(org.slug);
          membershipsByOrg[org.id] = membersResponse.data;
        } catch (error) {
          console.error(`Error fetching members for ${org.name}:`, error);
          membershipsByOrg[org.id] = [];
        }
      }));
      
      return membershipsByOrg;
    },
    enabled: !!organizationsList,
  });

  // Fetch users
  const { data: usersList, isLoading, error: fetchError } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await users.list();
      
      // Process user data from the API and add organization information
      return response.data.map((user: any) => {
        const userOrgs: OrganizationRole[] = [];
        
        // If we have organization and membership data
        if (organizationsList && memberships) {
          organizationsList.forEach((org: Organization) => {
            const orgMembers = memberships[org.id] || [];
            
            // Find this user's membership in this organization
            const membership = orgMembers.find(
              (m: Member) => m.user.email === user.email
            );
            
            if (membership) {
              userOrgs.push({
                organization_id: org.id,
                organization_name: org.name,
                role: membership.role.charAt(0).toUpperCase() + membership.role.slice(1)
              });
            }
          });
        }
        
        return {
          ...user,
          status: user.status || 'active',
          organizations: userOrgs,
          created_at: user.created_at || new Date().toISOString(),
          last_login: user.last_login || new Date().toISOString()
        };
      });
    },
    enabled: !!memberships,
  });

  // Initialize the auth user for demo purposes (this simulates storing the current user info)
  React.useEffect(() => {
    // Store current user in window for demo purposes
    if (user && !(window as any).authUser) {
      (window as any).authUser = user;
    }
  }, [user]);

  // Create user mutation
  const createMutation = useMutation({
    mutationFn: (newUser: any) => {
      // Only send the required fields to the user creation endpoint
      const userData = {
        email: newUser.email,
        full_name: newUser.name,
        password: newUser.password
      };
      return users.create(userData);
    },
    onSuccess: (data) => {
      const newUserId = data.data.id;
      // Handle memberships for the new user
      if (newUserId && formData.organizationMemberships.length > 0) {
        handleAddMemberships(newUserId, formData.organizationMemberships);
      }
      
      queryClient.invalidateQueries({ queryKey: ['users'] });
      handleClose();
      setSnackbar({ 
        open: true, 
        message: 'User created successfully', 
        severity: 'success' 
      });
    },
    onError: (error: any) => {
      setError(error.message || 'Failed to create user');
      setSnackbar({ 
        open: true, 
        message: `Error: ${error.message || 'Failed to create user'}`, 
        severity: 'error' 
      });
    },
  });

  // Update user mutation
  const updateMutation = useMutation({
    mutationFn: (updatedUser: any) => users.update(updatedUser.id, updatedUser),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      handleClose();
      setSnackbar({ 
        open: true, 
        message: 'User updated successfully', 
        severity: 'success' 
      });
    },
    onError: (error: any) => {
      setError(error.message || 'Failed to update user');
      setSnackbar({ 
        open: true, 
        message: `Error: ${error.message || 'Failed to update user'}`, 
        severity: 'error' 
      });
    },
  });

  // Delete user mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => users.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setSnackbar({ 
        open: true, 
        message: 'User deleted successfully', 
        severity: 'success' 
      });
    },
    onError: (error: any) => {
      setError(error.message || 'Failed to delete user');
      setSnackbar({ 
        open: true, 
        message: `Error: ${error.message || 'Failed to delete user'}`, 
        severity: 'error' 
      });
    },
  });

  const handleClickOpen = () => {
    setOpen(true);
    setEditUser(null);
    setFormData({
      name: '',
      email: '',
      password: '',
      is_admin: false,
      role: 'user',
      status: 'active',
      organizationMemberships: []
    });
    setError(null);
  };

  const handleEdit = (user: User) => {
    setEditUser(user);
    
    // Convert user organizations to organization memberships format
    const memberships = user.organizations ? [...user.organizations].map(org => ({
      organization_id: org.organization_id,
      organization_name: org.organization_name,
      role: org.role.toLowerCase()
    })) : [];
    
    setFormData({
      name: user.name,
      email: user.email,
      password: '',
      is_admin: user.is_admin,
      role: (user.organizations && user.organizations.length > 0) 
        ? user.organizations[0].role.toLowerCase() 
        : 'user',
      status: user.status || 'active',
      organizationMemberships: memberships
    });
    setOpen(true);
    setError(null);
  };

  const handleClose = () => {
    setOpen(false);
    setEditUser(null);
    setFormData({
      name: '',
      email: '',
      password: '',
      is_admin: false,
      role: 'user',
      status: 'active',
      organizationMemberships: []
    });
    setError(null);
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSubmit = (e: React.FormEvent) => {
    try {
      e.preventDefault();
      
      // Set is_admin based on role
      const submitData = {
        ...formData,
        is_admin: formData.role === 'admin'
      };
      
      if (editUser) {
        const updatedUser: { 
          id: string; 
          name: string; 
          email: string; 
          password?: string; 
          is_admin: boolean;
          role?: string;
          status?: string;
        } = {
          id: editUser.id,
          name: submitData.name,
          email: submitData.email,
          is_admin: submitData.is_admin,
          role: submitData.role,
          status: submitData.status
        };
        
        if (submitData.password) {
          updatedUser.password = submitData.password;
        }
        
        // First update the user
        updateMutation.mutate(updatedUser);
        
        // Then update the memberships
        handleUpdateMemberships(editUser.id, submitData.organizationMemberships);
      } else {
        // Create the user first, then handle memberships after success
        createMutation.mutate(submitData);
      }
    } catch (error) {
      console.error('Form submission error:', error);
    }
  };

  // Handle membership updates after user creation/update
  const handleUpdateMemberships = async (userId: string, memberships: OrganizationMembership[]) => {
    try {
      // Get current memberships from the API
      const userMemberships = usersList?.find((u: User) => u.id === userId)?.organizations || [];
      
      // Process each organization membership
      for (const membership of memberships) {
        // Find existing membership
        const existingMembership = userMemberships.find(
          (m: OrganizationRole) => m.organization_id === membership.organization_id
        );
        
        const orgData = organizationsList?.find(
          (org: Organization) => org.id === membership.organization_id
        );
        
        if (!orgData) continue; // Skip if organization not found
        
        // If membership exists, update it if role changed
        if (existingMembership) {
          if (existingMembership.role.toLowerCase() !== membership.role) {
            // Find the membership record ID from the memberships data
            const membershipRecords = memberships as any;
            const orgMembers = membershipRecords[membership.organization_id] || [];
            
            const memberRecord = orgMembers.find(
              (m: Member) => m.user.id.toString() === userId
            );
            
            if (memberRecord) {
              // Update the membership
              await organizations.members.update(
                orgData.slug,
                memberRecord.id,
                { role: membership.role }
              );
            }
          }
        } else {
          // Create new membership
          await organizations.members.create(
            orgData.slug,
            { 
              user_id: userId,
              role: membership.role
            }
          );
        }
      }
      
      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['users'] });
      queryClient.invalidateQueries({ queryKey: ['memberships'] });
      
      setSnackbar({ 
        open: true, 
        message: 'User organization memberships updated', 
        severity: 'success' 
      });
    } catch (error: any) {
      console.error('Error updating memberships:', error);
      setSnackbar({ 
        open: true, 
        message: `Error updating memberships: ${error.message || 'Unknown error'}`, 
        severity: 'error' 
      });
    }
  };

  // Handle membership creation after user creation
  const handleAddMemberships = async (userId: string, memberships: OrganizationMembership[]) => {
    try {
      // Process each organization membership
      for (const membership of memberships) {
        const orgData = organizationsList?.find(
          (org: Organization) => org.id === membership.organization_id
        );
        
        if (!orgData) continue; // Skip if organization not found
        
        // Create new membership with the expected payload format
        await organizations.members.create(
          orgData.slug,
          { 
            user_id: userId,
            role: membership.role
          }
        );
      }
      
      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['users'] });
      queryClient.invalidateQueries({ queryKey: ['memberships'] });
    } catch (error) {
      console.error('Error adding memberships:', error);
    }
  };

  // Handle adding organization membership in the form
  const handleAddOrganizationMembership = (organizationId: string) => {
    const organization = organizationOptions.find(org => org.id === organizationId);
    if (!organization || organization.id === 'all') return;
    
    // Check if this organization is already in the list
    if (formData.organizationMemberships.some(m => m.organization_id === organization.id)) {
      return; // Already in the list
    }
    
    setFormData({
      ...formData,
      organizationMemberships: [
        ...formData.organizationMemberships,
        {
          organization_id: organization.id,
          organization_name: organization.name,
          role: 'member' // Default role
        }
      ]
    });
  };
  
  // Handle removing organization membership from the form
  const handleRemoveOrganizationMembership = (organizationId: string) => {
    setFormData({
      ...formData,
      organizationMemberships: formData.organizationMemberships.filter(
        m => m.organization_id !== organizationId
      )
    });
  };
  
  // Handle changing a role for an organization membership
  const handleChangeOrganizationRole = (organizationId: string, role: string) => {
    setFormData({
      ...formData,
      organizationMemberships: formData.organizationMemberships.map(membership => 
        membership.organization_id === organizationId 
          ? { ...membership, role } 
          : membership
      )
    });
  };

  const handleDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      deleteMutation.mutate(id);
    }
  };

  const formatDate = (dateString?: string): string => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  // Helper functions for role display
  const getRoleDescription = (role: string): string => {
    const roleDescriptions: {[key: string]: string} = {
      'Admin': 'Full administrative access to all organization resources',
      'Developer': 'Can create and modify resources, deploy code',
      'Operator': 'Can manage and monitor operational resources',
      'Analyst': 'Can view and analyze data and reports',
      'Viewer': 'Read-only access to organization resources',
      'Support': 'Can handle support tickets and user assistance'
    };
    return roleDescriptions[role] || 'Standard access to organization resources';
  };

  const getRoleColor = (role: string): 'primary' | 'secondary' | 'success' | 'info' | 'warning' | 'default' => {
    const roleColors: {[key: string]: 'primary' | 'secondary' | 'success' | 'info' | 'warning' | 'default'} = {
      'Admin': 'primary',
      'Developer': 'secondary',
      'Operator': 'success',
      'Analyst': 'info',
      'Viewer': 'default',
      'Support': 'warning'
    };
    return roleColors[role] || 'default';
  };

  const getRoleIcon = (role: string) => {
    if (role === 'Admin') return <AdminIcon />;
    if (role === 'Developer') return <SecurityIcon />;
    if (role === 'Operator') return <SecurityIcon />;
    return <SecurityIcon />;
  };

  // Extract unique organizations from user data
  const getOrganizations = (): Organization[] => {
    if (!organizationsList) return [{ id: 'all', name: 'All Organizations', slug: 'all' }];
    
    const orgs = [{ id: 'all', name: 'All Organizations', slug: 'all' }];
    
    // Add real organizations from the API
    organizationsList.forEach((org: Organization) => {
      orgs.push({
        id: org.id,
        name: org.name,
        slug: org.slug
      });
    });
    
    return orgs;
  };

  // Filter users by selected organization
  const filterUsersByOrg = (users: User[]): User[] => {
    if (selectedOrg === 'all') return users;
    
    return users.filter(user => 
      user.organizations?.some(org => org.organization_id === selectedOrg)
    );
  };

  // Add the hasPermission function that was removed
  // Check if current user has admin or operator role
  const hasPermission = () => {
    // First check if user has global admin status
    if ((user as AuthUser | null)?.is_admin === true) {
      return true;
    }
    
    // Then check for admin role in any organization
    const currentUser = usersList?.find((u: User) => u.email === (user as AuthUser | null)?.email);
    if (currentUser?.organizations) {
      return currentUser.organizations.some((org: OrganizationRole) => 
        org.role === 'Admin' || org.role.toLowerCase() === 'admin'
      );
    }
    
    return false;
  };

  if (isLoading || orgsLoading || membershipsLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Users
        </Typography>
        <Typography>Loading users and organization data...</Typography>
      </Box>
    );
  }

  if (fetchError) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Users
        </Typography>
        <Alert severity="error">
          Error loading users: {(fetchError as Error).message}
        </Alert>
      </Box>
    );
  }

  // Get all available organizations
  const organizationOptions = getOrganizations();

  // Only show all users to admins/operators, otherwise show only the current user
  let filteredUsers = hasPermission() 
    ? usersList 
    : usersList?.filter((u: User) => u.email === user?.email);

  // Further filter by selected organization
  filteredUsers = filterUsersByOrg(filteredUsers || []);

  const displayedUsers = filteredUsers?.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  ) || [];

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Users Management
        </Typography>
        {hasPermission() && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleClickOpen}
          >
            Add User
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
          You can only view your own user information. Contact an administrator to see all users.
        </Alert>
      )}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          {selectedOrg === 'all' 
            ? 'All Organizations' 
            : `Organization: ${organizationOptions.find(org => org.id === selectedOrg)?.name}`}
        </Typography>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Filter by Organization</InputLabel>
          <Select
            value={selectedOrg}
            label="Filter by Organization"
            onChange={(e) => {
              setSelectedOrg(e.target.value);
              setPage(0); // Reset to first page when changing organization filter
            }}
          >
            {organizationOptions.map(org => (
              <MenuItem key={org.id} value={org.id}>{org.name}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      <Paper sx={{ width: '100%', mb: 2 }}>
        <TableContainer sx={{ maxHeight: 440 }}>
          <Table stickyHeader aria-label="users table">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Organization Roles</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Last Login</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {displayedUsers.map((user: User) => (
                <TableRow key={user.id} hover>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <PersonIcon sx={{ mr: 1, color: 'text.secondary' }} />
                      <Typography variant="body2">{user.name}</Typography>
                    </Box>
                  </TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      {(user.organizations && user.organizations.length > 0) ? (
                        user.organizations
                          .filter(org => selectedOrg === 'all' || org.organization_id === selectedOrg)
                          .map((org, index) => (
                            <Tooltip 
                              key={index} 
                              title={getRoleDescription(org.role)}
                              placement="right"
                            >
                              <Chip
                                size="small"
                                label={`${org.organization_name}: ${org.role}`}
                                color={getRoleColor(org.role)}
                                icon={getRoleIcon(org.role)}
                                sx={{ my: 0.5 }}
                              />
                            </Tooltip>
                          ))
                      ) : (
                        <Typography variant="body2" color="text.secondary">No organization roles</Typography>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      size="small"
                      label={(user.status ? user.status.charAt(0).toUpperCase() + user.status.slice(1) : 'Active')}
                      color={user.status === 'active' ? 'success' : 'error'}
                      icon={user.status === 'active' ? <VerifiedIcon /> : <BlockIcon />}
                    />
                  </TableCell>
                  <TableCell>{formatDate(user.last_login)}</TableCell>
                  <TableCell>
                    <Tooltip title="Edit User">
                      <IconButton
                        color="primary"
                        onClick={() => handleEdit(user)}
                        size="small"
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete User">
                      <IconButton
                        color="error"
                        onClick={() => handleDelete(user.id)}
                        size="small"
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
          count={filteredUsers?.length || 0}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>

      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>
          {editUser ? 'Edit User' : 'Add User'}
        </DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Name"
              type="text"
              fullWidth
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Email"
              type="email"
              fullWidth
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Password"
              type="password"
              fullWidth
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required={!editUser}
              helperText={editUser ? "Leave blank to keep current password" : ""}
              sx={{ mb: 2 }}
            />
            
            <FormControl fullWidth margin="dense" sx={{ mb: 2 }}>
              <InputLabel id="role-select-label">Role</InputLabel>
              <Select
                labelId="role-select-label"
                value={formData.role}
                label="Role"
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
              >
                <MenuItem value="user">User</MenuItem>
                <MenuItem value="operator">Operator</MenuItem>
                <MenuItem value="admin">Administrator</MenuItem>
              </Select>
            </FormControl>
            
            <FormControl fullWidth margin="dense" sx={{ mb: 2 }}>
              <InputLabel id="status-select-label">Status</InputLabel>
              <Select
                labelId="status-select-label"
                value={formData.status}
                label="Status"
                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              >
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
                <MenuItem value="suspended">Suspended</MenuItem>
              </Select>
            </FormControl>
            
            {/* Organization memberships section */}
            <Typography variant="subtitle1" gutterBottom sx={{ mt: 3 }}>
              Organization Memberships
            </Typography>
            
            {/* Display current organization memberships */}
            {formData.organizationMemberships.length > 0 ? (
              <Box sx={{ mb: 2 }}>
                {formData.organizationMemberships.map((membership, index) => (
                  <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Typography variant="body2" sx={{ flex: 1 }}>
                      {membership.organization_name}
                    </Typography>
                    <FormControl sx={{ width: 150, mx: 1 }}>
                      <InputLabel id={`role-label-${index}`}>Role</InputLabel>
                      <Select
                        labelId={`role-label-${index}`}
                        size="small"
                        value={membership.role}
                        label="Role"
                        onChange={(e) => handleChangeOrganizationRole(membership.organization_id, e.target.value)}
                      >
                        <MenuItem value="member">Member</MenuItem>
                        <MenuItem value="operator">Operator</MenuItem>
                        <MenuItem value="admin">Admin</MenuItem>
                      </Select>
                    </FormControl>
                    <IconButton 
                      size="small" 
                      color="error"
                      onClick={() => handleRemoveOrganizationMembership(membership.organization_id)}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Box>
                ))}
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                No organization memberships
              </Typography>
            )}
            
            {/* Add new organization membership */}
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <FormControl sx={{ flex: 1, mr: 1 }}>
                <InputLabel id="add-org-select-label">Select Organization</InputLabel>
                <Select
                  labelId="add-org-select-label"
                  id="add-org-select"
                  value=""
                  label="Select Organization"
                  onChange={(e) => {
                    const value = e.target.value;
                    if (value) {
                      handleAddOrganizationMembership(value);
                      // Reset the select value after adding
                      const selectElement = document.getElementById('add-org-select') as HTMLSelectElement;
                      if (selectElement) {
                        selectElement.value = '';
                      }
                    }
                  }}
                >
                  {organizationOptions
                    .filter(org => 
                      org.id !== 'all' && 
                      !formData.organizationMemberships.some(m => m.organization_id === org.id)
                    )
                    .map(org => (
                      <MenuItem key={org.id} value={org.id}>{org.name}</MenuItem>
                    ))
                  }
                </Select>
              </FormControl>
              <Button 
                variant="outlined" 
                startIcon={<AddIcon />}
                onClick={() => {
                  const select = document.getElementById('add-org-select') as HTMLSelectElement;
                  if (select && select.value) {
                    handleAddOrganizationMembership(select.value);
                    select.value = '';
                  }
                }}
              >
                Add
              </Button>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button
              type="submit"
              variant="contained"
              disabled={createMutation.isPending || updateMutation.isPending}
            >
              {editUser ? 'Update' : 'Create'}
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

export default Users; 