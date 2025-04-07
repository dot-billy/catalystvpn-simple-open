.PHONY: build test clean lint run

# Variables
BINARY_NAME=nebula-node-creator
VERSION=$(shell git describe --tags --always --dirty 2>/dev/null || echo "v0.0.0-$(shell git rev-parse --short HEAD)")
BUILD_DIR=build/$(VERSION)
BUILD_FLAGS=-ldflags "-X main.version=$(VERSION)"

# Build the application
build:
	@echo "Building version $(VERSION)..."
	@mkdir -p $(BUILD_DIR)
	@echo "Building for arm64 (Apple Silicon)..."
	GOOS=darwin GOARCH=arm64 go build $(BUILD_FLAGS) -o $(BUILD_DIR)/nebula-node-creator-arm64 ./cmd/nebula-node-creator
	@echo "Building for amd64 (Intel)..."
	GOOS=darwin GOARCH=amd64 go build $(BUILD_FLAGS) -o $(BUILD_DIR)/nebula-node-creator-amd64 ./cmd/nebula-node-creator
	@echo "Creating universal binary..."
	lipo -create -output $(BUILD_DIR)/nebula-node-creator $(BUILD_DIR)/nebula-node-creator-arm64 $(BUILD_DIR)/nebula-node-creator-amd64
	@echo "Build complete! Universal binary created in $(BUILD_DIR)/nebula-node-creator"

# Run tests
test:
	go test -v ./...

# Clean build artifacts
clean:
	go clean
	rm -rf build/

# Run linter
lint:
	golangci-lint run

# Run the application
run: build
	$(BUILD_DIR)/nebula-node-creator

# Install dependencies
deps:
	go mod tidy

# Build for multiple platforms
build-all: deps
	@mkdir -p $(BUILD_DIR)
	GOOS=linux GOARCH=amd64 go build $(BUILD_FLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-linux-amd64 ./cmd/nebula-node-creator
	GOOS=darwin GOARCH=amd64 go build $(BUILD_FLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-darwin-amd64 ./cmd/nebula-node-creator
	GOOS=windows GOARCH=amd64 go build $(BUILD_FLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-windows-amd64.exe ./cmd/nebula-node-creator

# Build universal binary for macOS
build-macos:
	@echo "Building universal binary version $(VERSION)..."
	@mkdir -p $(BUILD_DIR)
	GOOS=darwin GOARCH=arm64 go build $(BUILD_FLAGS) -o $(BUILD_DIR)/nebula-node-creator-arm64 ./cmd/nebula-node-creator
	GOOS=darwin GOARCH=amd64 go build $(BUILD_FLAGS) -o $(BUILD_DIR)/nebula-node-creator-amd64 ./cmd/nebula-node-creator
	lipo -create -output $(BUILD_DIR)/nebula-node-creator $(BUILD_DIR)/nebula-node-creator-arm64 $(BUILD_DIR)/nebula-node-creator-amd64
	@echo "Build complete! Binary: $(BUILD_DIR)/nebula-node-creator"

# Default target
all: deps lint test build 