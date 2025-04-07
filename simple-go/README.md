# Nebula Node Creator

A command-line tool for creating and managing Nebula VPN nodes. This tool helps automate the process of adding new nodes to your Nebula VPN network.

## Features

- Create new Nebula nodes with custom names and hostnames
- Interactive prompts for required information
- Secure credential handling
- Versioned builds with universal binary support for macOS
- Organized output structure for node information

## Prerequisites

- Go 1.21 or later
- Git
- macOS (for building universal binaries)

## Building

The project uses a Makefile for building and managing the application. Here are the available build targets:

### Building a Universal Binary (macOS)

To build a universal binary that works on both Apple Silicon and Intel Macs:

```bash
make build
```

This will:
1. Create a versioned build directory (e.g., `build/v0.1.0/`)
2. Build separate binaries for arm64 and amd64 architectures
3. Combine them into a universal binary using `lipo`
4. Output the final binary to `build/<version>/nebula-node-creator`

### Versioning

The build process automatically detects the version from git tags. To create a new version:

1. Commit your changes:
   ```bash
   git add .
   git commit -m "Your commit message"
   ```

2. Create a new tag:
   ```bash
   git tag -a v0.1.0 -m "Version description"
   ```

3. Build the new version:
   ```bash
   make build
   ```

### Other Build Targets

- `make test`: Run tests
- `make lint`: Run linter
- `make clean`: Clean build artifacts
- `make deps`: Install/update dependencies
- `make build-all`: Build for multiple platforms (Linux, macOS, Windows)
- `make run`: Build and run the application

## Usage

### Basic Usage

```bash
./build/v0.1.0/nebula-node-creator
```

The tool will prompt you for:
- Organization name
- Node name
- Node hostname

### Command Line Options

- `--version`: Display version information
- `--debug`: Enable debug logging

### Output

The tool creates a directory structure for each node:

```
output/
└── <node-id>/
    └── node.json
```

The `node.json` file contains all the information about the created node.

## Configuration

The tool can be configured using environment variables:

- `NEBULA_API_USERNAME`: API username
- `NEBULA_API_PASSWORD`: API password
- `NEBULA_ORG_NAME`: Organization name
- `NEBULA_API_BASE_URL`: API base URL (default: http://localhost:8000)

## Development

### Project Structure

```
.
├── cmd/
│   └── nebula-node-creator/
│       └── main.go
├── internal/
│   ├── api/
│   │   └── client.go
│   ├── config/
│   │   └── config.go
│   └── logger/
│       └── logger.go
├── Makefile
└── README.md
```

### Adding New Features

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Run tests and linter:
   ```bash
   make test
   make lint
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "Add your feature"
   ```

5. Create a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 