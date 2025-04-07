package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"

	"github.com/AlecAivazis/survey/v2"
)

const (
	baseURL = "http://localhost:8000"
)

type LoginRequest struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

type TokenResponse struct {
	Access  string `json:"access"`
	Refresh string `json:"refresh"`
}

type NodeRequest struct {
	Name     string `json:"name"`
	Hostname string `json:"hostname"`
}

type NodeResponse struct {
	ID           string      `json:"id"`
	Name         string      `json:"name"`
	Hostname     string      `json:"hostname"`
	NebulaIP     string      `json:"nebula_ip"`
	APIKey       string      `json:"api_key"`
	Organization string      `json:"organization"`
	Config       interface{} `json:"config"`
}

func main() {
	// Get credentials interactively
	var email string
	emailPrompt := &survey.Input{
		Message: "Enter your email:",
	}
	if err := survey.AskOne(emailPrompt, &email); err != nil {
		fmt.Printf("Error getting email: %v\n", err)
		return
	}

	var password string
	passwordPrompt := &survey.Password{
		Message: "Enter your password:",
	}
	if err := survey.AskOne(passwordPrompt, &password); err != nil {
		fmt.Printf("Error getting password: %v\n", err)
		return
	}

	var orgName string
	orgPrompt := &survey.Input{
		Message: "Enter organization name:",
	}
	if err := survey.AskOne(orgPrompt, &orgName); err != nil {
		fmt.Printf("Error getting organization name: %v\n", err)
		return
	}

	// Step 1: Get JWT token
	token, err := getToken(email, password)
	if err != nil {
		fmt.Printf("Error getting token: %v\n", err)
		return
	}

	// Step 2: Create node
	node, err := createNode(token, orgName)
	if err != nil {
		fmt.Printf("Error creating node: %v\n", err)
		return
	}

	// Step 3: Save node info
	err = saveNodeInfo(node, orgName)
	if err != nil {
		fmt.Printf("Error saving node info: %v\n", err)
		return
	}

	fmt.Println("Node created and info saved successfully!")
}

func getToken(email, password string) (string, error) {
	loginReq := LoginRequest{
		Email:    email,
		Password: password,
	}

	jsonData, err := json.Marshal(loginReq)
	if err != nil {
		return "", err
	}

	resp, err := http.Post(fmt.Sprintf("%s/api/token/", baseURL), "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("failed to get token: %s", string(body))
	}

	var tokenResp TokenResponse
	if err := json.NewDecoder(resp.Body).Decode(&tokenResp); err != nil {
		return "", err
	}

	return tokenResp.Access, nil
}

func createNode(token, orgName string) (*NodeResponse, error) {
	var name string
	namePrompt := &survey.Input{
		Message: "Enter node name:",
	}
	if err := survey.AskOne(namePrompt, &name); err != nil {
		return nil, err
	}

	var hostname string
	hostnamePrompt := &survey.Input{
		Message: "Enter node hostname:",
	}
	if err := survey.AskOne(hostnamePrompt, &hostname); err != nil {
		return nil, err
	}

	nodeReq := NodeRequest{
		Name:     name,
		Hostname: hostname,
	}

	jsonData, err := json.Marshal(nodeReq)
	if err != nil {
		return nil, err
	}

	req, err := http.NewRequest("POST", fmt.Sprintf("%s/api/organizations/%s/nodes/", baseURL, orgName), bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", token))
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("failed to create node: %s", string(body))
	}

	var node NodeResponse
	if err := json.NewDecoder(resp.Body).Decode(&node); err != nil {
		return nil, err
	}

	return &node, nil
}

func saveNodeInfo(node *NodeResponse, orgName string) error {
	// Create directory if it doesn't exist
	dirPath := filepath.Join("nebula", orgName)
	if err := os.MkdirAll(dirPath, 0755); err != nil {
		return err
	}

	// Save node info to JSON file
	filePath := filepath.Join(dirPath, "info.json")
	jsonData, err := json.MarshalIndent(node, "", "  ")
	if err != nil {
		return err
	}

	return os.WriteFile(filePath, jsonData, 0644)
}
