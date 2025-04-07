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
import { organizations, certificates } from '../services/api';
import { Certificate } from '../types';

const Certificates: React.FC = () => {
  const queryClient = useQueryClient();

  // First get the organizations
  const { data: orgs, isLoading: orgsLoading, error: orgsError } = useQuery({
    queryKey: ['organizations'],
    queryFn: async () => {
      try {
        const response = await organizations.list();
        return response.data;
      } catch (error) {
        console.error('Error fetching organizations:', error);
        return [];
      }
    },
  });

  // Get the first organization's ID to use for nested endpoints
  const orgId = orgs?.[0]?.id;

  // Get certificates for the first organization
  const { data, isLoading, error } = useQuery<Certificate[]>({
    queryKey: ['certificates', orgId],
    queryFn: async () => {
      if (!orgId) return [];
      try {
        const response = await certificates.list(orgId);
        return response.data;
      } catch (error) {
        console.error('Error fetching certificates:', error);
        throw error;
      }
    },
    enabled: !!orgId,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => certificates.revoke(orgId!, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['certificates', orgId] });
    },
  });

  if (orgsError) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Error loading organizations: {orgsError.message}
        </Alert>
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Error loading certificates: {error.message}
        </Alert>
      </Box>
    );
  }

  if (orgsLoading || isLoading) {
    return (
      <Box p={3}>
        <Skeleton variant="rectangular" height={400} />
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Certificates</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => {
            // TODO: Implement certificate creation
          }}
        >
          Add Certificate
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Expires</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data?.map((cert) => (
              <TableRow key={cert.id}>
                <TableCell>{cert.name}</TableCell>
                <TableCell>{cert.status}</TableCell>
                <TableCell>{new Date(cert.expires_at).toLocaleDateString()}</TableCell>
                <TableCell>
                  <IconButton
                    color="primary"
                    onClick={() => {
                      // TODO: Implement certificate editing
                    }}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    color="error"
                    onClick={() => deleteMutation.mutate(cert.id)}
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

export default Certificates; 