import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Paper, 
  Card, 
  CardContent, 
  CircularProgress 
} from '@mui/material';
import { organizations, networks, nodes, lighthouses } from '../services/api';

// Define types for our stats state
interface StatsState {
  organizations: number;
  networks: number;
  nodes: number;
  lighthouses: number;
  loading: boolean;
  error: string | null;
}

// Define type for StatCard props
interface StatCardProps {
  title: string;
  value: number;
  description: string;
}

// Dashboard with basic statistics
const Dashboard = () => {
  const [stats, setStats] = useState<StatsState>({
    organizations: 0,
    networks: 0,
    nodes: 0,
    lighthouses: 0,
    loading: true,
    error: null
  });

  // Fetch statistics data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setStats((prev: StatsState) => ({ ...prev, loading: true }));
        
        // Fetch counts from API
        let orgCount = 0;
        let networksCount = 0;
        let nodesCount = 0;
        let lighthousesCount = 0;
        
        try {
          // Get organizations
          const orgData = await organizations.list();
          orgCount = orgData.data?.length || 0;
          console.log('Organizations:', orgData.data);
          
          // If organizations exist, fetch their networks and nodes
          if (orgCount > 0 && orgData.data[0]) {
            // Use slug instead of ID
            const firstOrgSlug = orgData.data[0].slug;
            console.log('Using organization slug:', firstOrgSlug);
            
            try {
              // Use organization slug to request networks
              const networksData = await fetch(`http://myBackEndUrlOrIP:8000/api/organizations/${firstOrgSlug}/networks/`, {
                headers: {
                  'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
              });
              
              if (!networksData.ok) {
                throw new Error(`Network request failed with status ${networksData.status}`);
              }
              
              const networksJson = await networksData.json();
              console.log('Networks:', networksJson);
              networksCount = networksJson?.length || 0;
            } catch (networkError) {
              console.warn('Failed to fetch networks, continuing with count 0:', networkError);
            }
            
            try {
              // Use organization slug to request nodes
              const nodesData = await fetch(`http://myBackEndUrlOrIP:8000/api/organizations/${firstOrgSlug}/nodes/`, {
                headers: {
                  'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
              });
              
              if (!nodesData.ok) {
                throw new Error(`Nodes request failed with status ${nodesData.status}`);
              }
              
              const nodesJson = await nodesData.json();
              console.log('Nodes:', nodesJson);
              nodesCount = nodesJson?.length || 0;
            } catch (nodesError) {
              console.warn('Failed to fetch nodes, continuing with count 0:', nodesError);
            }
            
            try {
              // Use organization slug to request lighthouses
              const lighthousesData = await fetch(`http://myBackEndUrlOrIP:8000/api/organizations/${firstOrgSlug}/lighthouses/`, {
                headers: {
                  'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
              });
              
              if (!lighthousesData.ok) {
                throw new Error(`Lighthouses request failed with status ${lighthousesData.status}`);
              }
              
              const lighthousesJson = await lighthousesData.json();
              console.log('Lighthouses:', lighthousesJson);
              lighthousesCount = lighthousesJson?.length || 0;
            } catch (lighthouseError) {
              console.warn('Failed to fetch lighthouses, continuing with count 0:', lighthouseError);
            }
          }
        } catch (orgError) {
          console.warn('Failed to fetch organizations, continuing with count 0:', orgError);
        }
        
        // Update stats state - even if some requests failed
        setStats({
          organizations: orgCount,
          networks: networksCount,
          nodes: nodesCount,
          lighthouses: lighthousesCount,
          loading: false,
          error: null
        });
        
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setStats((prev: StatsState) => ({ 
          ...prev, 
          loading: false, 
          error: 'Failed to load dashboard data' 
        }));
      }
    };
    
    fetchData();
  }, []);

  // Stat card component
  const StatCard = ({ title, value, description }: StatCardProps) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          {title}
        </Typography>
        <Typography variant="h3" component="div" fontWeight="bold">
          {value}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          {description}
        </Typography>
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Dashboard
      </Typography>
      
      {stats.loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
          <CircularProgress />
        </Box>
      ) : stats.error ? (
        <Paper sx={{ p: 3, bgcolor: '#fff9f9' }}>
          <Typography color="error">{stats.error}</Typography>
        </Paper>
      ) : (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', margin: -1.5 }}>
          <Box sx={{ width: { xs: '100%', sm: '50%', md: '25%' }, padding: 1.5 }}>
            <StatCard 
              title="Organizations" 
              value={stats.organizations} 
              description="Total organizations in the system"
            />
          </Box>
          <Box sx={{ width: { xs: '100%', sm: '50%', md: '25%' }, padding: 1.5 }}>
            <StatCard 
              title="Networks" 
              value={stats.networks} 
              description="VPN networks deployed"
            />
          </Box>
          <Box sx={{ width: { xs: '100%', sm: '50%', md: '25%' }, padding: 1.5 }}>
            <StatCard 
              title="Nodes" 
              value={stats.nodes} 
              description="Active VPN nodes"
            />
          </Box>
          <Box sx={{ width: { xs: '100%', sm: '50%', md: '25%' }, padding: 1.5 }}>
            <StatCard 
              title="Lighthouses" 
              value={stats.lighthouses} 
              description="Discovery servers"
            />
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default Dashboard; 