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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Checkbox,
  Divider,
  Chip,
} from '@mui/material';
import { 
  Add as AddIcon, 
  Edit as EditIcon, 
  Delete as DeleteIcon,
  Group as GroupIcon,
  Computer as ComputerIcon,
  Lightbulb as LightbulbIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { organizations, securityGroups, nodes, lighthouses } from '../services/api';
import { SecurityGroup, Node, Lighthouse } from '../types';

interface SecurityGroupFormData {
  name: string;
  description: string;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const SecurityGroups: React.FC = () => {
  const queryClient = useQueryClient();
  const [openDialog, setOpenDialog] = useState(false);
  const [openMembersDialog, setOpenMembersDialog] = useState(false);
  const [editingGroup, setEditingGroup] = useState<SecurityGroup | null>(null);
  const [selectedGroup, setSelectedGroup] = useState<SecurityGroup | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [formData, setFormData] = useState<SecurityGroupFormData>({
    name: '',
    description: '',
  });
  const [selectedNodes, setSelectedNodes] = useState<string[]>([]);
  const [selectedLighthouses, setSelectedLighthouses] = useState<string[]>([]);

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

  // Get security groups for the first organization
  const { data, isLoading, error } = useQuery<SecurityGroup[]>({
    queryKey: ['securityGroups', orgId],
    queryFn: async () => {
      if (!orgId) return [];
      const response = await securityGroups.list(orgId);
      return response.data;
    },
    enabled: !!orgId,
  });

  // Get nodes for the first organization
  const { data: nodesList, isLoading: nodesLoading } = useQuery<Node[]>({
    queryKey: ['nodes', orgId],
    queryFn: async () => {
      if (!orgId) return [];
      const response = await nodes.list(orgId);
      return response.data;
    },
    enabled: !!orgId,
  });

  // Get lighthouses for the first organization
  const { data: lighthousesList, isLoading: lighthousesLoading } = useQuery<Lighthouse[]>({
    queryKey: ['lighthouses'],
    queryFn: async () => {
      const response = await lighthouses.list();
      return response.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: SecurityGroupFormData) => securityGroups.create(orgId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['securityGroups', orgId] });
      handleCloseDialog();
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: SecurityGroupFormData) => 
      securityGroups.update(orgId!, editingGroup!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['securityGroups', orgId] });
      handleCloseDialog();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => securityGroups.delete(orgId!, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['securityGroups', orgId] });
    },
  });

  const updateNodeMutation = useMutation({
    mutationFn: (data: { nodeId: string, securityGroupIds: string[] }) => 
      nodes.update(orgId!, data.nodeId, { security_group_ids: data.securityGroupIds }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nodes', orgId] });
      queryClient.invalidateQueries({ queryKey: ['securityGroups', orgId] });
    },
  });

  const updateLighthouseMutation = useMutation({
    mutationFn: (data: { lighthouseId: string, securityGroupIds: string[] }) => 
      lighthouses.update(data.lighthouseId, { security_group_ids: data.securityGroupIds }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lighthouses'] });
      queryClient.invalidateQueries({ queryKey: ['securityGroups', orgId] });
    },
  });

  const handleOpenDialog = (group?: SecurityGroup) => {
    if (group) {
      setEditingGroup(group);
      setFormData({
        name: group.name,
        description: group.description || '',
      });
    } else {
      setEditingGroup(null);
      setFormData({
        name: '',
        description: '',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingGroup(null);
    setFormData({
      name: '',
      description: '',
    });
  };

  const handleOpenMembersDialog = (group: SecurityGroup) => {
    setSelectedGroup(group);
    
    // Initialize selected nodes and lighthouses based on the security group
    // This is a simplification - in a real app, you would fetch the actual members
    // from the API or derive them from the security group data
    setSelectedNodes([]);
    setSelectedLighthouses([]);
    
    setOpenMembersDialog(true);
  };

  const handleCloseMembersDialog = () => {
    setOpenMembersDialog(false);
    setSelectedGroup(null);
    setSelectedNodes([]);
    setSelectedLighthouses([]);
    setTabValue(0);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingGroup) {
      updateMutation.mutate(formData);
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleNodeToggle = (nodeId: string) => {
    setSelectedNodes(prev => {
      if (prev.includes(nodeId)) {
        return prev.filter(id => id !== nodeId);
      } else {
        return [...prev, nodeId];
      }
    });
  };

  const handleLighthouseToggle = (lighthouseId: string) => {
    setSelectedLighthouses(prev => {
      if (prev.includes(lighthouseId)) {
        return prev.filter(id => id !== lighthouseId);
      } else {
        return [...prev, lighthouseId];
      }
    });
  };

  const handleSaveMembers = () => {
    if (!selectedGroup) return;

    // Update nodes
    nodesList?.forEach((node: Node) => {
      const isSelected = selectedNodes.includes(node.id);
      const currentGroups = node.security_groups || [];
      const hasGroup = currentGroups.some((g: SecurityGroup) => g.id === selectedGroup.id);
      
      if (isSelected && !hasGroup) {
        // Add to security group
        const newGroupIds = [...(node.security_group_ids || []), selectedGroup.id];
        updateNodeMutation.mutate({ nodeId: node.id, securityGroupIds: newGroupIds });
      } else if (!isSelected && hasGroup) {
        // Remove from security group
        const newGroupIds = (node.security_group_ids || []).filter((id: string) => id !== selectedGroup.id);
        updateNodeMutation.mutate({ nodeId: node.id, securityGroupIds: newGroupIds });
      }
    });

    // Update lighthouses
    lighthousesList?.forEach((lighthouse: Lighthouse) => {
      const isSelected = selectedLighthouses.includes(lighthouse.id);
      const currentGroups = lighthouse.security_groups || [];
      const hasGroup = currentGroups.some((g: SecurityGroup) => g.id === selectedGroup.id);
      
      if (isSelected && !hasGroup) {
        // Add to security group
        const newGroupIds = [...(lighthouse.security_group_ids || []), selectedGroup.id];
        updateLighthouseMutation.mutate({ lighthouseId: lighthouse.id, securityGroupIds: newGroupIds });
      } else if (!isSelected && hasGroup) {
        // Remove from security group
        const newGroupIds = (lighthouse.security_group_ids || []).filter((id: string) => id !== selectedGroup.id);
        updateLighthouseMutation.mutate({ lighthouseId: lighthouse.id, securityGroupIds: newGroupIds });
      }
    });

    handleCloseMembersDialog();
  };

  if (orgsLoading) {
    return (
      <Box>
        <Skeleton variant="text" width={200} height={40} />
        <Skeleton variant="rectangular" width="100%" height={400} />
      </Box>
    );
  }

  if (orgsError) {
    return (
      <Alert severity="error">
        Error loading organizations: {(orgsError as Error).message}
      </Alert>
    );
  }

  if (!orgId) {
    return (
      <Alert severity="info">
        No organizations found. Please create an organization first.
      </Alert>
    );
  }

  if (isLoading) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Security Groups
        </Typography>
        <Skeleton variant="rectangular" width="100%" height={400} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Error loading security groups: {(error as Error).message}
      </Alert>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h4">Security Groups</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Security Group
        </Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data?.map((group: SecurityGroup) => (
              <TableRow key={group.id}>
                <TableCell>{group.name}</TableCell>
                <TableCell>{group.description}</TableCell>
                <TableCell>
                  <IconButton
                    onClick={() => handleOpenMembersDialog(group)}
                    title="Manage Members"
                  >
                    <GroupIcon />
                  </IconButton>
                  <IconButton
                    onClick={() => handleOpenDialog(group)}
                    title="Edit"
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    onClick={() => {
                      if (window.confirm('Are you sure you want to delete this security group?')) {
                        deleteMutation.mutate(group.id);
                      }
                    }}
                    title="Delete"
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Create/Edit Security Group Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <form onSubmit={handleSubmit}>
          <DialogTitle>
            {editingGroup ? 'Edit Security Group' : 'Create Security Group'}
          </DialogTitle>
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
            />
            <TextField
              margin="dense"
              label="Description"
              type="text"
              fullWidth
              multiline
              rows={4}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button type="submit" variant="contained">
              {editingGroup ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Manage Members Dialog */}
      <Dialog 
        open={openMembersDialog} 
        onClose={handleCloseMembersDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Manage Members: {selectedGroup?.name}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange} aria-label="member tabs">
              <Tab icon={<ComputerIcon />} label="Nodes" />
              <Tab icon={<LightbulbIcon />} label="Lighthouses" />
            </Tabs>
          </Box>
          
          <TabPanel value={tabValue} index={0}>
            <List>
              {nodesList?.map((node) => (
                <ListItem key={node.id} divider>
                  <ListItemText 
                    primary={node.name} 
                    secondary={`IP: ${node.ip_address || 'N/A'}`} 
                  />
                  <ListItemSecondaryAction>
                    <Checkbox
                      edge="end"
                      checked={selectedNodes.includes(node.id)}
                      onChange={() => handleNodeToggle(node.id)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
              {(!nodesList || nodesList.length === 0) && (
                <ListItem>
                  <ListItemText primary="No nodes found" />
                </ListItem>
              )}
            </List>
          </TabPanel>
          
          <TabPanel value={tabValue} index={1}>
            <List>
              {lighthousesList?.map((lighthouse) => (
                <ListItem key={lighthouse.id} divider>
                  <ListItemText 
                    primary={lighthouse.name} 
                    secondary={`IP: ${lighthouse.ip_address || 'N/A'}`} 
                  />
                  <ListItemSecondaryAction>
                    <Checkbox
                      edge="end"
                      checked={selectedLighthouses.includes(lighthouse.id)}
                      onChange={() => handleLighthouseToggle(lighthouse.id)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
              {(!lighthousesList || lighthousesList.length === 0) && (
                <ListItem>
                  <ListItemText primary="No lighthouses found" />
                </ListItem>
              )}
            </List>
          </TabPanel>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseMembersDialog}>Cancel</Button>
          <Button 
            onClick={handleSaveMembers} 
            variant="contained"
            disabled={updateNodeMutation.isPending || updateLighthouseMutation.isPending}
          >
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SecurityGroups; 