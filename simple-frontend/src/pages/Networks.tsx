import React from 'react';
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
} from '@mui/material';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { organizations, networks } from '../services/api';
import { Network } from '../types';

const Networks: React.FC = () => {
  const queryClient = useQueryClient();

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

  // Get networks for the first organization
  const { data, isLoading, error } = useQuery<Network[]>({
    queryKey: ['networks', orgId],
    queryFn: async () => {
      if (!orgId) return [];
      const response = await networks.list(orgId);
      return response.data;
    },
    enabled: !!orgId,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => networks.delete(orgId!, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['networks', orgId] });
    },
  });

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
          Networks
        </Typography>
        <Skeleton variant="rectangular" width="100%" height={400} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Error loading networks: {(error as Error).message}
      </Alert>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h4">Networks</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => {
            // TODO: Implement create network
          }}
        >
          Add Network
        </Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>CIDR</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data?.map((network: Network) => (
              <TableRow key={network.id}>
                <TableCell>{network.name}</TableCell>
                <TableCell>{network.cidr}</TableCell>
                <TableCell>{network.description}</TableCell>
                <TableCell>
                  <IconButton
                    onClick={() => {
                      // TODO: Implement edit network
                    }}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    onClick={() => {
                      if (window.confirm('Are you sure you want to delete this network?')) {
                        deleteMutation.mutate(network.id);
                      }
                    }}
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default Networks; 