import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Typography,
  Paper,
  Card,
  CardContent,
  CardHeader,
  Divider,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Avatar,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Tabs,
  Tab,
  Checkbox,
  Tooltip,
  Alert,
  LinearProgress,
  Grid as MuiGrid,
  Stack,
  MenuItem,
  Autocomplete
} from '@mui/material';
import Grid from '../components/CustomGrid';
import {
  Business as BusinessIcon,
  Hub as HubIcon,
  Lightbulb as LightbulbIcon,
  Security as SecurityIcon,
  VpnKey as VpnKeyIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  CloudDownload as CloudDownloadIcon,
  Refresh as RefreshIcon,
  Computer as ComputerIcon,
  ArrowBack as ArrowBackIcon,
  CalendarToday as CalendarIcon,
  Info as InfoIcon,
  Language as LanguageIcon
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { organizations, networks, nodes, lighthouses, securityGroups, certificates } from '../services/api';
import { Node, Lighthouse, SecurityGroup } from '../types';

interface Resource {
  id: string;
  name: string;
  status?: string;
  ip_address?: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
  node_ids?: string[];
  lighthouse_ids?: string[];
  firewall_rule_ids?: string[];
  firewall_rules?: Array<{
    id: string;
    rule_type: string;
    protocol: string;
    port?: number;
    cidr?: string;
  }>;
}

interface SecurityGroupFormData {
  id?: string;
  name: string;
  description: string;
  node_ids: string[];
  lighthouse_ids: string[];
  firewall_rule_ids: string[];
  firewall_rules?: FirewallRuleForm[];
  orgSlug?: string;
}

interface FirewallRule {
  id: string;
  rule_type: string;
  protocol: string;
  port?: number;
  host: string;
  cidr: string;
  local_cidr: string;
  group: string;
  groups: string[];
  ca_name: string;
  ca_sha: string;
}

interface SecurityGroupDetails {
  id: string;
  organization: string;
  name: string;
  description: string;
  firewall_rules: FirewallRule[];
  nodes: string[];
  lighthouses: string[];
}

interface FirewallRuleForm {
  rule_type: 'inbound' | 'outbound';
  protocol: 'tcp' | 'udp';
  port: string;
  cidr: string;
}

interface DraggableItem {
  id: string;
  name: string;
  hostname: string;
  type: 'node' | 'lighthouse';
}

const OrganizationDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogType, setDialogType] = useState<string>('');
  const [formData, setFormData] = useState<SecurityGroupFormData>({
    name: '',
    description: '',
    node_ids: [],
    lighthouse_ids: [],
    firewall_rule_ids: [],
  });
  const [tabValue, setTabValue] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [selectedSecurityGroupId, setSelectedSecurityGroupId] = useState<string | null>(null);
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const [availableSelectedItems, setAvailableSelectedItems] = useState<Set<string>>(new Set());
  const [selectedSelectedItems, setSelectedSelectedItems] = useState<Set<string>>(new Set());

  // Fetch organizations first to get the correct org with slug
  const { data: organizations, isLoading: orgsLoading } = useQuery({
    queryKey: ['organizations'],
    queryFn: async () => {
      try {
        const response = await fetch('http://myBackEndUrlOrIP:8000/api/organizations/?include_counts=true', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
          }
        });
        
        if (!response.ok) {
          throw new Error(`Organizations request failed with status ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Organizations list:', data);
        return data;
      } catch (error) {
        console.error('Error fetching organizations:', error);
        throw error;
      }
    },
  });

  // Find the organization that matches the id from URL params
  const organization = organizations?.find((org: any) => org.id === id);
  const orgSlug = organization?.slug;

  console.log('Fetched Organization:', organization);
  console.log('Organization Slug:', orgSlug);

  // Add new query for security group details after orgSlug is defined
  const { data: securityGroupDetails } = useQuery({
    queryKey: ['securityGroupDetails', selectedSecurityGroupId, orgSlug],
    queryFn: async () => {
      if (!selectedSecurityGroupId || !orgSlug) return null;
      try {
        const response = await fetch(`http://myBackEndUrlOrIP:8000/api/organizations/${orgSlug}/security-groups/${selectedSecurityGroupId}/`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
          }
        });
        if (!response.ok) {
          throw new Error(`Failed to fetch security group details with status ${response.status}`);
        }
        return response.json();
      } catch (error) {
        console.error('Error fetching security group details:', error);
        return null;
      }
    },
    enabled: !!selectedSecurityGroupId && !!orgSlug
  });

  // Fetch organization details using slug
  const { data: org, isLoading: orgLoading, error: orgError } = useQuery({
    queryKey: ['organization', id, orgSlug],
    queryFn: async () => {
      if (!orgSlug) {
        throw new Error('Organization slug not found');
      }
      try {
        const response = await fetch(`http://myBackEndUrlOrIP:8000/api/organizations/${orgSlug}/`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
          }
        });
        
        if (!response.ok) {
          throw new Error(`Organization details request failed with status ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Organization details:', data);
        return data;
      } catch (error) {
        console.error('Error fetching organization details:', error);
        throw error;
      }
    },
    enabled: !!orgSlug,
  });

  // Fetch networks using slug
  const { data: networksList, isLoading: networksLoading, error: networksError } = useQuery({
    queryKey: ['networks', id, orgSlug],
    queryFn: async () => {
      if (!orgSlug) {
        throw new Error('Organization slug not found');
      }
      try {
        const response = await fetch(`http://myBackEndUrlOrIP:8000/api/organizations/${orgSlug}/networks/`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
          }
        });
        
        if (!response.ok) {
          console.warn(`Networks request failed with status ${response.status}`);
          return []; // Return empty array instead of throwing to avoid breaking the UI
        }
        
        const data = await response.json();
        console.log('Networks:', data);
        return data;
      } catch (error) {
        console.error('Error fetching networks:', error);
        return []; // Return empty array
      }
    },
    enabled: !!orgSlug,
  });

  // Fetch nodes using slug
  const { data: nodesList, isLoading: nodesLoading, error: nodesError } = useQuery({
    queryKey: ['nodes', id, orgSlug],
    queryFn: async () => {
      if (!orgSlug) {
        throw new Error('Organization slug not found');
      }
      try {
        const response = await fetch(`http://myBackEndUrlOrIP:8000/api/organizations/${orgSlug}/nodes/`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
          }
        });
        
        if (!response.ok) {
          console.warn(`Nodes request failed with status ${response.status}`);
          return []; // Return empty array instead of throwing
        }
        
        const data = await response.json();
        console.log('Nodes:', data);
        return data;
      } catch (error) {
        console.error('Error fetching nodes:', error);
        return []; // Return empty array
      }
    },
    enabled: !!orgSlug,
  });

  // Fetch lighthouses using slug
  const { data: lighthousesList, isLoading: lighthousesLoading, error: lighthousesError } = useQuery({
    queryKey: ['lighthouses', id, orgSlug],
    queryFn: async () => {
      if (!orgSlug) {
        throw new Error('Organization slug not found');
      }
      try {
        const response = await fetch(`http://myBackEndUrlOrIP:8000/api/organizations/${orgSlug}/lighthouses/`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
          }
        });
        
        if (!response.ok) {
          console.warn(`Lighthouses request failed with status ${response.status}`);
          return []; // Return empty array instead of throwing
        }
        
        const data = await response.json();
        console.log('Lighthouses:', data);
        return data;
      } catch (error) {
        console.error('Error fetching lighthouses:', error);
        return []; // Return empty array
      }
    },
    enabled: !!orgSlug,
  });

  // Fetch security groups using slug
  const { data: securityGroupsList, isLoading: securityGroupsLoading, error: securityGroupsError } = useQuery({
    queryKey: ['securityGroups', id, orgSlug],
    queryFn: async () => {
      if (!orgSlug) {
        throw new Error('Organization slug not found');
      }
      try {
        const response = await fetch(`http://myBackEndUrlOrIP:8000/api/organizations/${orgSlug}/security-groups/`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
          }
        });
        
        if (!response.ok) {
          console.warn(`Security groups request failed with status ${response.status}`);
          return []; // Return empty array instead of throwing
        }
        
        const data = await response.json();
        console.log('Security Groups:', data);
        return data;
      } catch (error) {
        console.error('Error fetching security groups:', error);
        return []; // Return empty array
      }
    },
    enabled: !!orgSlug,
  });

  // Fetch certificates using slug
  const { data: certificatesList, isLoading: certificatesLoading, error: certificatesError } = useQuery({
    queryKey: ['certificates', id, orgSlug],
    queryFn: async () => {
      if (!orgSlug) {
        throw new Error('Organization slug not found');
      }
      try {
        const response = await fetch(`http://myBackEndUrlOrIP:8000/api/organizations/${orgSlug}/certificates/`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
          }
        });
        
        if (!response.ok) {
          console.warn(`Certificates request failed with status ${response.status}`);
          return []; // Return empty array instead of throwing
        }
        
        const data = await response.json();
        console.log('Certificates:', data);
        return data;
      } catch (error) {
        console.error('Error fetching certificates:', error);
        return []; // Return empty array
      }
    },
    enabled: !!orgSlug,
  });

  // Add firewall rules query
  const { data: firewallRulesList } = useQuery({
    queryKey: ['firewallRules', orgSlug],
    queryFn: async () => {
      if (!orgSlug) return [];
      try {
        const response = await fetch(`http://myBackEndUrlOrIP:8000/api/organizations/${orgSlug}/firewall-rules/`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
          }
        });
        if (!response.ok) {
          throw new Error(`Failed to fetch firewall rules with status ${response.status}`);
        }
        return response.json();
      } catch (error) {
        console.error('Error fetching firewall rules:', error);
        return [];
      }
    },
    enabled: !!orgSlug
  });

  // Handle dialog opening
  const handleOpenDialog = (type: string, item?: any) => {
    setDialogType(type);
    if (item) {
      // Editing existing item
        setFormData({
          id: item.id,
          name: item.name,
          description: item.description || '',
        node_ids: item.node_ids || [],
        lighthouse_ids: item.lighthouse_ids || [],
        firewall_rule_ids: item.firewall_rule_ids || [],
        orgSlug: orgSlug
        });
      } else {
      // Creating new item
        setFormData({
        id: '',
        name: '',
        description: '',
        node_ids: [],
        lighthouse_ids: [],
        firewall_rule_ids: [],
        orgSlug: orgSlug
      });
    }
    setOpenDialog(true);
  };

  // Handle dialog closing
  const handleCloseDialog = () => {
    setOpenDialog(false);
    setDialogType('');
    setFormData({
      name: '',
      description: '',
      node_ids: [],
      lighthouse_ids: [],
      firewall_rule_ids: [],
      orgSlug: orgSlug
    });
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleGoBack = () => {
    navigate('/organizations');
  };

  const handleEditOrg = () => {
    // Implement organization editing
    setError(null);
    handleOpenDialog('organization', org);
  };

  const handleDeleteOrg = () => {
    if (window.confirm(`Are you sure you want to delete the organization "${org?.name}"? This action cannot be undone.`)) {
      // Implement organization deletion
    }
  };

  const handleSave = async () => {
    if (!formData.name || !formData.description) {
      setError('Name and description are required');
      return;
    }

    try {
      const authToken = localStorage.getItem('authToken');
      if (!authToken) {
        throw new Error('No authentication token found');
      }

      // Request data with just the basic properties
      const requestData = {
        name: formData.name,
        description: formData.description
      };

      console.log(`${formData.id ? 'Updating' : 'Creating'} security group:`, requestData);

      // Determine if we're creating a new security group or updating an existing one
      const isNewSecurityGroup = !formData.id;
      
      const url = isNewSecurityGroup
        ? `http://myBackEndUrlOrIP:8000/api/organizations/${formData.orgSlug}/security-groups/`
        : `http://myBackEndUrlOrIP:8000/api/organizations/${formData.orgSlug}/security-groups/${formData.id}/`;
      
      const method = isNewSecurityGroup ? 'POST' : 'PATCH';

      console.log(`Making ${method} request to: ${url}`);
      
      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        // Improved error handling for non-JSON responses
        try {
          const contentType = response.headers.get('content-type');
          if (contentType && contentType.includes('application/json')) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Failed to ${isNewSecurityGroup ? 'create' : 'update'} security group with status ${response.status}`);
          } else {
            const errorText = await response.text();
            console.error('Non-JSON error response:', errorText);
            throw new Error(`Failed to ${isNewSecurityGroup ? 'create' : 'update'} security group with status ${response.status}`);
          }
        } catch (parseError) {
          console.error('Error parsing response:', parseError);
          throw new Error(`Failed to ${isNewSecurityGroup ? 'create' : 'update'} security group with status ${response.status}. Server returned a non-JSON response.`);
        }
      }

      // Try to parse the response as JSON, but handle errors gracefully
      let result;
      try {
        result = await response.json();
        console.log(`Security group ${isNewSecurityGroup ? 'created' : 'updated'} successfully:`, result);
      } catch (jsonError) {
        console.warn('Could not parse response as JSON:', jsonError);
        // Continue execution since the main operation was successful
      }

      // If we need to update nodes, lighthouses, or firewall rules, we should use separate API endpoints
      // For now, we're just updating the basic security group info

      // Invalidate the security groups query to refresh the list
      queryClient.invalidateQueries({ queryKey: ['securityGroups', id, orgSlug] });
      
      // Close the dialog and reset form
      handleCloseDialog();
      setFormData({
        id: '',
        name: '',
        description: '',
        node_ids: [],
        lighthouse_ids: [],
        firewall_rule_ids: [],
        orgSlug: orgSlug || ''
      });
    } catch (error) {
      console.error('Error saving security group:', error);
      setError(error instanceof Error ? error.message : 'Failed to save security group');
    }
  };

  const ResourceList = ({ title, items, icon, type, error }: { title: string; items: Resource[]; icon: React.ReactNode; type: string; error?: any }) => {
    const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

    const toggleExpand = (itemId: string) => {
      setExpandedItems(prev => {
        const newSet = new Set(prev);
        if (newSet.has(itemId)) {
          newSet.delete(itemId);
          setSelectedSecurityGroupId(null);
        } else {
          newSet.add(itemId);
          setSelectedSecurityGroupId(itemId);
        }
        return newSet;
      });
    };

    return (
      <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardHeader
        title={title}
        avatar={<Avatar sx={{ bgcolor: 'primary.main' }}>{icon}</Avatar>}
        action={
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog(type.toLowerCase().replace(' ', ''))}
            size="small"
            sx={{ 
              whiteSpace: 'nowrap',
              minWidth: { xs: 'auto', sm: '120px' }
            }}
          >
            <Box sx={{ display: { xs: 'none', sm: 'inline' } }}>Add {type}</Box>
            <AddIcon sx={{ display: { xs: 'inline', sm: 'none' } }} />
          </Button>
        }
      />
      <Divider />
        <CardContent sx={{ flexGrow: 1, overflow: 'auto', p: 0 }}>
          {error ? (
            <Alert severity="error" sx={{ m: 2 }}>
              Error loading {title.toLowerCase()}: {error.message}
            </Alert>
          ) : (
            <List dense>
          {items?.map((item) => (
                <React.Fragment key={item.id}>
            <ListItem 
              sx={{
                flexDirection: { xs: 'column', sm: 'row' },
                alignItems: { xs: 'flex-start', sm: 'center' },
                      borderBottom: '1px solid rgba(0,0,0,0.06)',
                      py: 1.5,
                      cursor: 'pointer'
                    }}
                    onClick={() => type === 'Security Group' && toggleExpand(item.id)}
                    secondaryAction={
                      <Box sx={{ 
                        display: 'flex',
                        gap: 1,
                        ml: { xs: 0, sm: 'auto' },
                        mt: { xs: 1, sm: 0 }
                      }}>
                        <Tooltip title={`Edit ${type}`}>
                          <IconButton 
                            size="small"
                            color="primary"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleOpenDialog(type.toLowerCase().replace(' ', ''), item);
                            }}
                          >
                            <EditIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title={`Delete ${type}`}>
                          <IconButton 
                            size="small"
                            color="error"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    }
            >
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center',
                      width: '100%'
              }}>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                  {item.status ? (
                    <Tooltip title={item.status}>
                      {item.status.toLowerCase() === 'active' ? (
                              <CheckCircleIcon color="success" fontSize="small" />
                      ) : item.status.toLowerCase() === 'inactive' ? (
                              <ErrorIcon color="error" fontSize="small" />
                      ) : (
                              <WarningIcon color="warning" fontSize="small" />
                      )}
                    </Tooltip>
                  ) : (
                          React.cloneElement(icon as React.ReactElement, { fontSize: 'small' })
                  )}
                </ListItemIcon>
                <ListItemText
                        primary={
                          <Typography variant="subtitle2">
                            {item.name}
                            {item.created_at && (
                              <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                                (Added {new Date(item.created_at).toLocaleDateString()})
                              </Typography>
                            )}
                          </Typography>
                        }
                  secondary={
                          <Stack spacing={0.5} sx={{ mt: 0.5 }}>
                      {item.description && (
                              <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
                          {item.description}
                        </Typography>
                      )}
                      {item.ip_address && (
                              <Chip 
                                icon={<LanguageIcon />} 
                                label={item.ip_address} 
                                size="small" 
                                variant="outlined" 
                                sx={{ maxWidth: '100%' }}
                              />
                            )}
                          </Stack>
                        }
                        sx={{ m: 0 }}
                />
              </Box>
                  </ListItem>
                  {type === 'Security Group' && expandedItems.has(item.id) && (
              <Box sx={{ 
                      pl: 2, 
                      pr: 2, 
                      pb: 2,
                      borderBottom: '1px solid rgba(0,0,0,0.06)',
                      backgroundColor: 'rgba(0,0,0,0.02)'
                    }}>
                      <Typography variant="subtitle2" sx={{ mb: 1, mt: 1 }}>
                        Security Group Details
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                          <Typography variant="body2" color="text.secondary">
                            <strong>Nodes:</strong>
                          </Typography>
                          <List dense>
                            {securityGroupDetails?.nodes?.map((nodeId: string) => {
                              const node = nodesList?.find((n: Node) => n.id === nodeId);
                              return (
                                <ListItem key={nodeId} sx={{ py: 0.5 }}>
                                  <ListItemIcon sx={{ minWidth: 30 }}>
                                    <ComputerIcon fontSize="small" />
                                  </ListItemIcon>
                                  <ListItemText
                                    primary={node?.name || 'Unknown Node'}
                                    secondary={node?.hostname}
                                  />
                                </ListItem>
                              );
                            })}
                            {(!securityGroupDetails?.nodes || securityGroupDetails.nodes.length === 0) && (
                              <ListItem>
                                <ListItemText primary="No nodes assigned" />
                              </ListItem>
                            )}
                          </List>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <Typography variant="body2" color="text.secondary">
                            <strong>Lighthouses:</strong>
                          </Typography>
                          <List dense>
                            {securityGroupDetails?.lighthouses?.map((lighthouseId: string) => {
                              const lighthouse = lighthousesList?.find((l: Lighthouse) => l.id === lighthouseId);
                              return (
                                <ListItem key={lighthouseId} sx={{ py: 0.5 }}>
                                  <ListItemIcon sx={{ minWidth: 30 }}>
                                    <LightbulbIcon fontSize="small" />
                                  </ListItemIcon>
                                  <ListItemText
                                    primary={lighthouse?.name || 'Unknown Lighthouse'}
                                    secondary={lighthouse?.hostname}
                                  />
                                </ListItem>
                              );
                            })}
                            {(!securityGroupDetails?.lighthouses || securityGroupDetails.lighthouses.length === 0) && (
                              <ListItem>
                                <ListItemText primary="No lighthouses assigned" />
                              </ListItem>
                            )}
                          </List>
                        </Grid>
                        <Grid item xs={12}>
                          <Typography variant="body2" color="text.secondary">
                            <strong>Firewall Rules:</strong>
                          </Typography>
                          <List dense>
                            {securityGroupDetails?.firewall_rules?.map((rule: FirewallRule) => (
                              <ListItem key={rule.id} sx={{ py: 0.5 }}>
                                <ListItemIcon sx={{ minWidth: 30 }}>
                                  <SecurityIcon fontSize="small" />
                                </ListItemIcon>
                                <ListItemText
                                  primary={`${rule.rule_type} - ${rule.protocol}`}
                                  secondary={
                                    <>
                                      <Typography variant="body2" component="span">
                                        Port: {rule.port || 'Any'} | 
                                        Host: {rule.host || 'Any'} | 
                                        CIDR: {rule.cidr || 'Any'}
                                      </Typography>
                                      {rule.local_cidr && (
                                        <Typography variant="body2" component="div">
                                          Local CIDR: {rule.local_cidr}
                                        </Typography>
                                      )}
                                      {rule.ca_name && (
                                        <Typography variant="body2" component="div">
                                          CA: {rule.ca_name} (SHA: {rule.ca_sha})
                                        </Typography>
                                      )}
                                    </>
                                  }
                                />
            </ListItem>
                            ))}
                            {(!securityGroupDetails?.firewall_rules || securityGroupDetails.firewall_rules.length === 0) && (
                              <ListItem>
                                <ListItemText primary="No firewall rules assigned" />
                              </ListItem>
                            )}
                          </List>
                        </Grid>
                      </Grid>
                    </Box>
                  )}
                </React.Fragment>
          ))}

          {(!items || items.length === 0) && (
            <ListItem>
              <ListItemText
                primary={`No ${title.toLowerCase()} found`}
                secondary={`Click the + button to add a new ${type.toLowerCase()}`}
              />
            </ListItem>
          )}
        </List>
          )}
      </CardContent>
    </Card>
  );
  };

  const TabPanel = (props: { children?: React.ReactNode; index: number; value: number }) => {
    const { children, value, index, ...other } = props;
  
    return (
      <div
        role="tabpanel"
        hidden={value !== index}
        id={`organization-tabpanel-${index}`}
        aria-labelledby={`organization-tab-${index}`}
        {...other}
      >
        {value === index && (
          <Box sx={{ py: 2 }}>
            {children}
          </Box>
        )}
      </div>
    );
  };

  const a11yProps = (index: number) => {
    return {
      id: `organization-tab-${index}`,
      'aria-controls': `organization-tabpanel-${index}`,
    };
  };

  const handleDragStart = (e: React.DragEvent<HTMLLIElement>, item: DraggableItem) => {
    e.dataTransfer.setData('text/plain', JSON.stringify(item));
  };

  const handleDrop = (e: React.DragEvent<HTMLLIElement>, isSelectedSection: boolean) => {
    e.preventDefault();
    const item = JSON.parse(e.dataTransfer.getData('text/plain')) as DraggableItem;
    
    setFormData(prev => {
      const newFormData = { ...prev };
      if (isSelectedSection) {
        // Moving to selected section
        if (item.type === 'node') {
          if (!newFormData.node_ids.includes(item.id)) {
            newFormData.node_ids = [...newFormData.node_ids, item.id];
          }
        } else {
          if (!newFormData.lighthouse_ids.includes(item.id)) {
            newFormData.lighthouse_ids = [...newFormData.lighthouse_ids, item.id];
          }
        }
      } else {
        // Moving to available section
        if (item.type === 'node') {
          newFormData.node_ids = newFormData.node_ids.filter(id => id !== item.id);
        } else {
          newFormData.lighthouse_ids = newFormData.lighthouse_ids.filter(id => id !== item.id);
        }
      }
      return newFormData;
    });
  };

  const DraggableList = ({ 
    items, 
    onDragStart, 
    onDragOver, 
    onDrop,
    selectedItems,
    onSelect,
    isSelectedSection = false
  }: { 
    items: DraggableItem[]; 
    onDragStart: (e: React.DragEvent<HTMLLIElement>, item: DraggableItem) => void;
    onDragOver: (e: React.DragEvent<HTMLLIElement>) => void;
    onDrop: (e: React.DragEvent<HTMLLIElement>) => void;
    selectedItems: Set<string>;
    onSelect: (item: DraggableItem) => void;
    isSelectedSection?: boolean;
  }) => (
    <List dense>
      {items.map((item) => (
        <ListItem
          key={item.id}
          draggable
          onDragStart={(e: React.DragEvent<HTMLLIElement>) => onDragStart(e, item)}
          onDragOver={(e: React.DragEvent<HTMLLIElement>) => e.preventDefault()}
          onDrop={(e: React.DragEvent<HTMLLIElement>) => onDrop(e)}
          onClick={() => onSelect(item)}
          sx={{
            cursor: 'move',
            backgroundColor: selectedItems.has(item.id) ? 'rgba(25, 118, 210, 0.08)' : 'inherit',
            '&:hover': { 
              backgroundColor: selectedItems.has(item.id) 
                ? 'rgba(25, 118, 210, 0.12)' 
                : 'rgba(0, 0, 0, 0.04)' 
            }
          }}
        >
          <ListItemIcon>
            {item.type === 'node' ? <ComputerIcon /> : <LightbulbIcon />}
          </ListItemIcon>
          <ListItemText
            primary={item.name}
            secondary={item.hostname}
          />
        </ListItem>
      ))}
    </List>
  );

  const FirewallRuleBuilder = ({ 
    rule, 
    onChange 
  }: { 
    rule: FirewallRuleForm; 
    onChange: (rule: FirewallRuleForm) => void;
  }) => {
    const [localRule, setLocalRule] = useState<FirewallRuleForm>(rule);

    const handlePortChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const newPort = e.target.value;
      setLocalRule(prev => ({ ...prev, port: newPort }));
    };

    const handleAddRule = () => {
      if (localRule.port && localRule.rule_type && localRule.protocol && localRule.cidr) {
        onChange(localRule);
        setLocalRule({
          rule_type: 'inbound',
          protocol: 'tcp',
          port: '',
          cidr: '0.0.0.0/0'
        });
      }
    };

    return (
      <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <TextField
              select
              fullWidth
              label="Rule Type"
              value={localRule.rule_type}
              onChange={(e) => setLocalRule(prev => ({ ...prev, rule_type: e.target.value as 'inbound' | 'outbound' }))}
            >
              <MenuItem value="inbound">Inbound</MenuItem>
              <MenuItem value="outbound">Outbound</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Port"
              value={localRule.port}
              onChange={handlePortChange}
              inputProps={{
                inputMode: 'numeric',
                pattern: '[0-9]*'
              }}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              select
              fullWidth
              label="Protocol"
              value={localRule.protocol}
              onChange={(e) => setLocalRule(prev => ({ ...prev, protocol: e.target.value as 'tcp' | 'udp' }))}
            >
              <MenuItem value="tcp">TCP</MenuItem>
              <MenuItem value="udp">UDP</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="CIDR"
              value={localRule.cidr}
              onChange={(e) => setLocalRule(prev => ({ ...prev, cidr: e.target.value }))}
              placeholder="0.0.0.0/0"
            />
          </Grid>
          <Grid item xs={12}>
            <Button
              variant="contained"
              onClick={handleAddRule}
              disabled={!localRule.port || !localRule.rule_type || !localRule.protocol || !localRule.cidr}
              fullWidth
            >
              Add Rule
            </Button>
          </Grid>
        </Grid>
      </Box>
    );
  };

  if (orgLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Loading organization details...
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  if (orgError) {
  return (
    <Box sx={{ p: 3 }}>
        <Button 
          startIcon={<ArrowBackIcon />}
          onClick={handleGoBack}
          sx={{ mb: 2 }}
        >
          Back to Organizations
        </Button>
        <Alert severity="error" sx={{ mb: 3 }}>
          Error loading organization: {(orgError as Error).message}
        </Alert>
        <Button 
          variant="contained" 
          onClick={() => queryClient.invalidateQueries({ queryKey: ['organization', id] })}
        >
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Back button and error display */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Button 
          startIcon={<ArrowBackIcon />}
          onClick={handleGoBack}
        >
          Back to Organizations
        </Button>
        
        {error && (
          <Alert 
            severity="error" 
            sx={{ ml: 2, flexGrow: 1 }}
            onClose={() => setError(null)}
          >
            {error}
          </Alert>
        )}
      </Box>
      
      {/* Organization Header */}
      <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
        <Box sx={{ 
          display: 'flex', 
          flexDirection: { xs: 'column', sm: 'row' },
          alignItems: { xs: 'flex-start', sm: 'center' }, 
          mb: 2,
          gap: 2
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Avatar sx={{ bgcolor: 'primary.main', mr: 2, width: 56, height: 56 }}>
              <BusinessIcon sx={{ fontSize: 32 }} />
            </Avatar>
            <Box>
            <Typography variant="h4" component="h1" sx={{ 
              fontSize: { xs: '1.5rem', sm: '2rem', md: '2.125rem' }
            }}>
              {org?.name}
            </Typography>
              
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mt: 0.5 }}>
                <Chip
                  size="small"
                  label={org?.slug || org?.id?.substring(0, 8)}
                  variant="outlined"
                />
                
                <Tooltip title="Organization Status">
                  <Chip
                    size="small"
                    color={org?.status === 'inactive' ? 'error' : 'success'}
                    label={org?.status || 'active'}
                  />
                </Tooltip>
          </Box>
            </Box>
          </Box>
          
          <Box sx={{ 
            ml: { xs: 0, sm: 'auto' },
            display: 'flex',
            gap: 1,
            alignSelf: { xs: 'flex-end', sm: 'center' }
          }}>
            <Tooltip title="Edit Organization">
              <IconButton onClick={handleEditOrg}>
                <EditIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Delete Organization">
              <IconButton color="error" onClick={handleDeleteOrg}>
                <DeleteIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        
        <Typography color="text.secondary" sx={{ mb: 3 }}>
          {org?.description || 'No description provided'}
        </Typography>
        
        <Divider sx={{ mb: 3 }} />
        
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', width: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <HubIcon fontSize="small" sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="subtitle2">Networks</Typography>
      </Box>
                <Typography variant="h4" color="primary.main" sx={{ fontWeight: 'bold' }}>
                  {networksList?.length || 0}
                </Typography>
                {networksLoading && <LinearProgress sx={{ mt: 1 }} />}
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', width: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <ComputerIcon fontSize="small" sx={{ mr: 1, color: 'info.main' }} />
                  <Typography variant="subtitle2">Nodes</Typography>
                </Box>
                <Typography variant="h4" color="info.main" sx={{ fontWeight: 'bold' }}>
                  {nodesList?.length || 0}
                </Typography>
                {nodesLoading && <LinearProgress sx={{ mt: 1 }} />}
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', width: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <LightbulbIcon fontSize="small" sx={{ mr: 1, color: 'warning.main' }} />
                  <Typography variant="subtitle2">Lighthouses</Typography>
                </Box>
                <Typography variant="h4" color="warning.main" sx={{ fontWeight: 'bold' }}>
                  {lighthousesList?.length || 0}
                </Typography>
                {lighthousesLoading && <LinearProgress sx={{ mt: 1 }} />}
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', width: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <SecurityIcon fontSize="small" sx={{ mr: 1, color: 'success.main' }} />
                  <Typography variant="subtitle2">Security Groups</Typography>
                </Box>
                <Typography variant="h4" color="success.main" sx={{ fontWeight: 'bold' }}>
                  {securityGroupsList?.length || 0}
                </Typography>
                {securityGroupsLoading && <LinearProgress sx={{ mt: 1 }} />}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 1 }}>
          <Chip 
            icon={<CalendarIcon fontSize="small" />}
            label={`Created: ${org?.created_at ? new Date(org.created_at).toLocaleDateString() : 'Unknown'}`} 
            size="small" 
            variant="outlined"
          />
          {org?.updated_at && (
            <Chip
              icon={<RefreshIcon fontSize="small" />}
              label={`Updated: ${new Date(org.updated_at).toLocaleDateString()}`} 
              size="small" 
              variant="outlined"
            />
          )}
        </Box>
      </Paper>

      {/* Tabs Navigation */}
      <Box sx={{ width: '100%', mb: 2 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange} 
            aria-label="organization resources tabs"
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab label="Networks" icon={<HubIcon />} iconPosition="start" {...a11yProps(0)} />
            <Tab label="Nodes" icon={<ComputerIcon />} iconPosition="start" {...a11yProps(1)} />
            <Tab label="Lighthouses" icon={<LightbulbIcon />} iconPosition="start" {...a11yProps(2)} />
            <Tab label="Security Groups" icon={<SecurityIcon />} iconPosition="start" {...a11yProps(3)} />
            <Tab label="Certificates" icon={<VpnKeyIcon />} iconPosition="start" {...a11yProps(4)} />
          </Tabs>
        </Box>
        
        <TabPanel value={tabValue} index={0}>
          <ResourceList
            title="Networks"
            items={networksList || []}
            icon={<HubIcon />}
            type="Network"
            error={networksError}
          />
        </TabPanel>
        
        <TabPanel value={tabValue} index={1}>
          <ResourceList
            title="Nodes"
            items={nodesList || []}
            icon={<ComputerIcon />}
            type="Node"
            error={nodesError}
          />
        </TabPanel>
        
        <TabPanel value={tabValue} index={2}>
          <ResourceList
            title="Lighthouses"
            items={lighthousesList || []}
            icon={<LightbulbIcon />}
            type="Lighthouse"
            error={lighthousesError}
          />
        </TabPanel>
        
        <TabPanel value={tabValue} index={3}>
          <ResourceList
            title="Security Groups"
            items={securityGroupsList || []}
            icon={<SecurityIcon />}
            type="Security Group"
            error={securityGroupsError}
          />
        </TabPanel>
        
        <TabPanel value={tabValue} index={4}>
          <ResourceList
            title="Certificates"
            items={certificatesList || []}
            icon={<VpnKeyIcon />}
            type="Certificate"
            error={certificatesError}
          />
        </TabPanel>
      </Box>

      {/* Add/Edit Resource Dialog */}
      <Dialog 
        open={openDialog} 
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
          <DialogTitle>
          {`${formData.name ? 'Edit' : 'Add'} ${dialogType.charAt(0).toUpperCase() + dialogType.slice(1)}`}
          </DialogTitle>
          <DialogContent>
          <Box component="form" noValidate sx={{ mt: 1 }}>
              <TextField
              margin="normal"
              required
                fullWidth
              id="name"
              label="Name"
              name="name"
              autoFocus
                value={formData.name}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, name: e.target.value })}
              />
              <TextField
              margin="normal"
                fullWidth
              id="description"
              label="Description"
              name="description"
                multiline
                rows={4}
                value={formData.description}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, description: e.target.value })}
            />
            
            {dialogType === 'securitygroup' && (
              <>
                <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>
                  Members
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Paper variant="outlined" sx={{ p: 1, height: '100%' }}>
                      <Typography variant="subtitle2" sx={{ mb: 1 }}>
                        Available
                      </Typography>
                      <TextField
                        fullWidth
                        size="small"
                        placeholder="Search..."
                        sx={{ mb: 1 }}
                      />
                      <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
                        <DraggableList
                          items={[
                            ...(nodesList?.filter((node: Node) => !formData.node_ids.includes(node.id)).map((node: Node) => ({
                              id: node.id,
                              name: node.name,
                              hostname: node.hostname,
                              type: 'node' as const
                            })) || []),
                            ...(lighthousesList?.filter((lh: Lighthouse) => !formData.lighthouse_ids.includes(lh.id)).map((lh: Lighthouse) => ({
                              id: lh.id,
                              name: lh.name,
                              hostname: lh.hostname,
                              type: 'lighthouse' as const
                            })) || [])
                          ]}
                          onDragStart={handleDragStart}
                          onDragOver={(e) => e.preventDefault()}
                          onDrop={(e) => handleDrop(e, false)}
                          selectedItems={availableSelectedItems}
                          onSelect={(item) => {
                            const newSelected = new Set(availableSelectedItems);
                            if (newSelected.has(item.id)) {
                              newSelected.delete(item.id);
                            } else {
                              newSelected.add(item.id);
                            }
                            setAvailableSelectedItems(newSelected);
                          }}
                          isSelectedSection={false}
                        />
                      </Box>
                      <Button 
                        variant="contained"
                        onClick={() => {
                          // Create a new copy of the form data to trigger re-render
                          const newFormData = { ...formData };
                          
                          // Add selected items to appropriate arrays
                          availableSelectedItems.forEach(id => {
                            const node = nodesList?.find((n: Node) => n.id === id);
                            const lighthouse = lighthousesList?.find((l: Lighthouse) => l.id === id);
                            
                            if (node && !newFormData.node_ids.includes(id)) {
                              newFormData.node_ids.push(id);
                            } else if (lighthouse && !newFormData.lighthouse_ids.includes(id)) {
                              newFormData.lighthouse_ids.push(id);
                            }
                          });
                          
                          // Update form data and clear selections
                          setFormData(newFormData);
                          setAvailableSelectedItems(new Set());
                        }}
                        disabled={availableSelectedItems.size === 0}
                        fullWidth
                        sx={{ mt: 1 }}
                      >
                        Add Selected
                      </Button>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Paper variant="outlined" sx={{ p: 1, height: '100%' }}>
                      <Typography variant="subtitle2" sx={{ mb: 1 }}>
                        Selected
                      </Typography>
                      <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
                        <DraggableList
                          items={[
                            ...(nodesList?.filter((node: Node) => formData.node_ids.includes(node.id)).map((node: Node) => ({
                              id: node.id,
                              name: node.name,
                              hostname: node.hostname,
                              type: 'node' as const
                            })) || []),
                            ...(lighthousesList?.filter((lh: Lighthouse) => formData.lighthouse_ids.includes(lh.id)).map((lh: Lighthouse) => ({
                              id: lh.id,
                              name: lh.name,
                              hostname: lh.hostname,
                              type: 'lighthouse' as const
                            })) || [])
                          ]}
                          onDragStart={handleDragStart}
                          onDragOver={(e) => e.preventDefault()}
                          onDrop={(e) => handleDrop(e, true)}
                          selectedItems={selectedSelectedItems}
                          onSelect={(item) => {
                            const newSelected = new Set(selectedSelectedItems);
                            if (newSelected.has(item.id)) {
                              newSelected.delete(item.id);
                            } else {
                              newSelected.add(item.id);
                            }
                            setSelectedSelectedItems(newSelected);
                          }}
                          isSelectedSection={true}
                        />
                      </Box>
                      <Button
                        variant="contained"
                        onClick={() => {
                          // Create a new copy of the form data to trigger re-render
                          const newFormData = { ...formData };
                          
                          // Remove selected items from both arrays
                          newFormData.node_ids = newFormData.node_ids.filter(id => !selectedSelectedItems.has(id));
                          newFormData.lighthouse_ids = newFormData.lighthouse_ids.filter(id => !selectedSelectedItems.has(id));
                          
                          // Update form data and clear selections
                          setFormData(newFormData);
                          setSelectedSelectedItems(new Set());
                        }}
                        disabled={selectedSelectedItems.size === 0}
                        fullWidth
                        sx={{ mt: 1 }}
                      >
                        Remove Selected
                      </Button>
                    </Paper>
                  </Grid>
                </Grid>

                <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>
                  Firewall Rules
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <FirewallRuleBuilder
                    rule={{
                      rule_type: 'inbound',
                      protocol: 'tcp',
                      port: '',
                      cidr: '0.0.0.0/0'
                    }}
                    onChange={(newRule) => {
                      setFormData({
                        ...formData,
                        firewall_rules: [...(formData.firewall_rules || []), newRule]
                      });
                    }}
                  />
                </Box>
                <List>
                  {formData.firewall_rules?.map((rule: FirewallRuleForm, index: number) => (
                    <ListItem key={index}>
                      <ListItemText
                        primary={`${rule.rule_type} - ${rule.protocol}:${rule.port}`}
                        secondary={`CIDR: ${rule.cidr}`}
                      />
                      <IconButton
                        edge="end"
                        onClick={() => {
                          setFormData({
                            ...formData,
                            firewall_rules: formData.firewall_rules?.filter((_: FirewallRuleForm, i: number) => i !== index)
                          });
                        }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </ListItem>
                  ))}
                </List>
              </>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button variant="contained" onClick={handleSave}>
            Save
            </Button>
          </DialogActions>
      </Dialog>
    </Box>
  );
};

export default OrganizationDetails; 