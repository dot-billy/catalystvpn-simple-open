package api

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/billymuller/simple-go/internal/config"
	"github.com/stretchr/testify/assert"
)

func TestNewClient(t *testing.T) {
	cfg := &config.Config{
		API: config.API{
			BaseURL: "http://localhost:8000",
		},
	}

	client := NewClient(cfg)
	assert.NotNil(t, client)
	assert.Equal(t, "http://localhost:8000", client.baseURL)
	assert.NotNil(t, client.client)
}

func TestLogin(t *testing.T) {
	// Create a test server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "/api/token/", r.URL.Path)
		assert.Equal(t, "application/json", r.Header.Get("Content-Type"))

		var req struct {
			Email    string `json:"email"`
			Password string `json:"password"`
		}
		err := json.NewDecoder(r.Body).Decode(&req)
		assert.NoError(t, err)

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]string{
			"access": "test-token",
		})
	}))
	defer server.Close()

	// Create config with test server URL
	cfg := &config.Config{
		API: config.API{
			BaseURL: server.URL,
		},
	}

	client := NewClient(cfg)
	token, err := client.Login("test@example.com", "password")
	assert.NoError(t, err)
	assert.Equal(t, "test-token", token)
}

func TestCreateNode(t *testing.T) {
	// Create a test server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "/api/organizations/test-org/nodes/", r.URL.Path)
		assert.Equal(t, "Bearer test-token", r.Header.Get("Authorization"))
		assert.Equal(t, "application/json", r.Header.Get("Content-Type"))

		var req NodeRequest
		err := json.NewDecoder(r.Body).Decode(&req)
		assert.NoError(t, err)
		assert.Equal(t, "test-node", req.Name)
		assert.Equal(t, "test.example.com", req.Hostname)

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(NodeResponse{
			ID:           "40217527-d795-4f8d-a8d0-6f938130d77b",
			Name:         "test-node",
			Hostname:     "test.example.com",
			NebulaIP:     "10.0.0.1",
			APIKey:       "test-api-key",
			Organization: "test-org",
		})
	}))
	defer server.Close()

	// Create config with test server URL
	cfg := &config.Config{
		API: config.API{
			BaseURL: server.URL,
		},
		Organization: config.Organization{
			Name: "test-org",
		},
	}

	client := NewClient(cfg)
	node, err := client.CreateNode("test-token", "test-org", &NodeRequest{
		Name:     "test-node",
		Hostname: "test.example.com",
	})
	assert.NoError(t, err)
	assert.Equal(t, "40217527-d795-4f8d-a8d0-6f938130d77b", node.ID)
	assert.Equal(t, "test-node", node.Name)
	assert.Equal(t, "test.example.com", node.Hostname)
	assert.Equal(t, "10.0.0.1", node.NebulaIP)
	assert.Equal(t, "test-api-key", node.APIKey)
	assert.Equal(t, "test-org", node.Organization)
}
