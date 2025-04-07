package api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/billymuller/simple-go/internal/config"
)

// Client represents the API client
type Client struct {
	baseURL string
	client  *http.Client
}

// NewClient creates a new API client
func NewClient(cfg *config.Config) *Client {
	return &Client{
		baseURL: cfg.API.BaseURL,
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// Login authenticates with the API and returns a JWT token
func (c *Client) Login(username, password string) (string, error) {
	loginReq := struct {
		Email    string `json:"email"`
		Password string `json:"password"`
	}{
		Email:    username,
		Password: password,
	}

	jsonData, err := json.Marshal(loginReq)
	if err != nil {
		return "", fmt.Errorf("failed to marshal login request: %w", err)
	}

	resp, err := c.client.Post(
		fmt.Sprintf("%s/api/token/", c.baseURL),
		"application/json",
		bytes.NewBuffer(jsonData),
	)
	if err != nil {
		return "", fmt.Errorf("failed to make login request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("login failed with status %d: %s", resp.StatusCode, string(body))
	}

	var tokenResp struct {
		Access string `json:"access"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&tokenResp); err != nil {
		return "", fmt.Errorf("failed to decode token response: %w", err)
	}

	return tokenResp.Access, nil
}

// CreateNode creates a new node in the organization
func (c *Client) CreateNode(token, orgName string, nodeReq *NodeRequest) (*NodeResponse, error) {
	jsonData, err := json.Marshal(nodeReq)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal node request: %w", err)
	}

	req, err := http.NewRequest(
		"POST",
		fmt.Sprintf("%s/api/organizations/%s/nodes/", c.baseURL, orgName),
		bytes.NewBuffer(jsonData),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", token))
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("failed to create node with status %d: %s", resp.StatusCode, string(body))
	}

	var node NodeResponse
	if err := json.NewDecoder(resp.Body).Decode(&node); err != nil {
		return nil, fmt.Errorf("failed to decode node response: %w", err)
	}

	return &node, nil
}

// NodeRequest represents the request body for creating a node
type NodeRequest struct {
	Name     string `json:"name"`
	Hostname string `json:"hostname"`
}

// NodeResponse represents the response from creating a node
type NodeResponse struct {
	ID           string      `json:"id"`
	Name         string      `json:"name"`
	Hostname     string      `json:"hostname"`
	NebulaIP     string      `json:"nebula_ip"`
	APIKey       string      `json:"api_key"`
	Organization string      `json:"organization"`
	Config       interface{} `json:"config"`
}
