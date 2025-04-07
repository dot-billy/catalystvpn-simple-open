export interface Organization {
  id: string;
  name: string;
  description?: string;
}

export interface Network {
  id: string;
  name: string;
  cidr: string;
  description?: string;
}

export interface Node {
  id: string;
  name: string;
  hostname: string;
  ip_address: string;
  status: string;
  security_groups: SecurityGroup[];
  security_group_ids?: string[];
  organization_id?: string;
  network_id?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Lighthouse {
  id: string;
  name: string;
  hostname: string;
  ip_address: string;
  status: string;
  security_groups: SecurityGroup[];
  security_group_ids?: string[];
  organization_id?: string;
  network_id?: string;
  created_at?: string;
  updated_at?: string;
}

export interface SecurityGroup {
  id: string;
  name: string;
  description?: string;
  organization_id?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Certificate {
  id: string;
  name: string;
  type: string;
  status: string;
  expires_at: string;
  organization_id?: string;
  created_at?: string;
  updated_at?: string;
} 