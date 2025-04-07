package main

import (
	"encoding/json"
	"io/ioutil"
	"os"
	"path/filepath"

	"github.com/AlecAivazis/survey/v2"
	"github.com/billymuller/simple-go/internal/api"
	"github.com/billymuller/simple-go/internal/config"
	"github.com/billymuller/simple-go/internal/logger"
	"github.com/rs/zerolog/log"
	"github.com/spf13/cobra"
)

var (
	cfg     *config.Config
	version = "dev" // This will be set by the build process
)

func main() {
	cfg = config.NewConfig()

	rootCmd := &cobra.Command{
		Use:     "nebula-node-creator",
		Short:   "Create Nebula nodes",
		Version: version,
		Long: `A command-line tool for creating and managing Nebula VPN nodes.
This tool helps automate the process of adding new nodes to your Nebula VPN network.`,
		PersistentPreRun: func(cmd *cobra.Command, args []string) {
			debug, _ := cmd.Flags().GetBool("debug")
			logger.InitLogger(debug)
		},
		Run: runCreate,
	}

	rootCmd.PersistentFlags().Bool("debug", false, "Enable debug logging")
	rootCmd.SetVersionTemplate("{{.Name}} version {{.Version}}\n")

	createCmd := &cobra.Command{
		Use:   "create",
		Short: "Create a new node",
		Long:  "Create a new node in the specified organization",
		Run:   runCreate,
	}

	createCmd.Flags().String("name", "", "Name of the node")
	createCmd.Flags().String("hostname", "", "Hostname of the node")
	createCmd.MarkFlagRequired("name")
	createCmd.MarkFlagRequired("hostname")

	rootCmd.AddCommand(createCmd)

	if err := rootCmd.Execute(); err != nil {
		log.Fatal().Err(err).Msg("Failed to execute command")
	}
}

func runCreate(cmd *cobra.Command, args []string) {
	// Prompt for organization name if not set
	if cfg.Organization.Name == "" {
		prompt := &survey.Input{
			Message: "Enter organization name:",
		}
		if err := survey.AskOne(prompt, &cfg.Organization.Name); err != nil {
			log.Fatal().Err(err).Msg("Failed to get organization name")
		}
	}

	// Prompt for node name
	var nodeName string
	prompt := &survey.Input{
		Message: "Enter node name:",
	}
	if err := survey.AskOne(prompt, &nodeName); err != nil {
		log.Fatal().Err(err).Msg("Failed to get node name")
	}

	// Prompt for node hostname
	var nodeHostname string
	prompt = &survey.Input{
		Message: "Enter node hostname:",
	}
	if err := survey.AskOne(prompt, &nodeHostname); err != nil {
		log.Fatal().Err(err).Msg("Failed to get node hostname")
	}

	// Create API client
	client := api.NewClient(cfg)

	// Login
	token, err := client.Login(cfg.API.Username, cfg.API.Password)
	if err != nil {
		log.Fatal().Err(err).Msg("Failed to login")
	}

	// Create node
	node, err := client.CreateNode(token, cfg.Organization.Name, &api.NodeRequest{
		Name:     nodeName,
		Hostname: nodeHostname,
	})
	if err != nil {
		log.Fatal().Err(err).Msg("Failed to create node")
	}

	// Create output directory
	outputDir := filepath.Join(cfg.Output.BaseDir, node.ID)
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		log.Fatal().Err(err).Msg("Failed to create output directory")
	}

	// Save node information
	nodePath := filepath.Join(outputDir, "node.json")
	nodeData, err := json.MarshalIndent(node, "", "  ")
	if err != nil {
		log.Fatal().Err(err).Msg("Failed to marshal node data")
	}

	if err := ioutil.WriteFile(nodePath, nodeData, 0644); err != nil {
		log.Fatal().Err(err).Msg("Failed to save node information")
	}

	log.Info().
		Str("node_id", node.ID).
		Str("path", nodePath).
		Msg("Node created successfully")
}
