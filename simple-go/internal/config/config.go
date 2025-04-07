package config

import (
	"os"
	"path/filepath"
)

// API holds API-related configuration
type API struct {
	BaseURL  string
	Username string
	Password string
}

// Organization holds organization-related configuration
type Organization struct {
	Name string
}

// Output holds output-related configuration
type Output struct {
	BaseDir string
}

// Config holds all configuration for the application
type Config struct {
	API          API
	Organization Organization
	Output       Output
}

// NewConfig creates a new configuration with defaults and environment overrides
func NewConfig() *Config {
	cfg := &Config{}

	// API Configuration
	cfg.API.BaseURL = getEnvOrDefault("NEBULA_API_URL", "http://localhost:8000")
	cfg.API.Username = getEnvOrDefault("NEBULA_API_USERNAME", "")
	cfg.API.Password = getEnvOrDefault("NEBULA_API_PASSWORD", "")

	// Organization Configuration
	cfg.Organization.Name = getEnvOrDefault("NEBULA_ORG_NAME", "")

	// Output Configuration
	cfg.Output.BaseDir = getEnvOrDefault("NEBULA_OUTPUT_DIR", "nebula")

	return cfg
}

// GetNodeInfoPath returns the path where node information should be saved
func (c *Config) GetNodeInfoPath() string {
	return filepath.Join(c.Output.BaseDir, c.Organization.Name, "info.json")
}

// GetNodeDirPath returns the directory path for node information
func (c *Config) GetNodeDirPath() string {
	return filepath.Join(c.Output.BaseDir, c.Organization.Name)
}

func getEnvOrDefault(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}
