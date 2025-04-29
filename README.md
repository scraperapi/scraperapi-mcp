# ScraperAPI MCP server

The ScraperAPI MCP server enables LLMs to retrieve and process web scraping requests using the ScraperAPI service.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Development](#development)

## Features

- Full implementation of the Model Context Protocol specification
- Seamless integration with ScraperAPI for web scraping
- Simple setup with Docker or Python

## Architecture

```
          ┌───────────────┐     ┌───────────────────────┐     ┌───────────────┐
          │  LLM Client   │────▶│  Scraper MCP Server   │────▶│    AI Model   │
          └───────────────┘     └───────────────────────┘     └───────────────┘
                                            │
                                            ▼
                                  ┌──────────────────┐
                                  │  ScraperAPI API  │
                                  └──────────────────┘
```

## Installation

### Prerequisites

- Python 3.11+ or Docker

### Using uv (recommended)

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will
use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *scraperapi-mcp-server*.

### Using PIP

Alternatively you can install `scraperapi-mcp-server` via pip:

```bash
pip install scraperapi-mcp-server
```

After installation, you can run it as a script using:

```bash
python -m scraperapi-mcp-server
```

### Using Docker

You can build and run the MCP server using Docker:

```bash
# Build the Docker image
docker build -t scraperapi-mcp-server .

# Run the Docker container
docker run -i --rm scraperapi-mcp-server
```

Alternatively, you can use docker-compose:

```bash
# Build and run with docker-compose
docker-compose up --build

# Or in detached mode
docker-compose up --build -d
```

## Configuration

### Configure for Claude Desktop App

Add to your Claude Desktop App settings:

#### Using uvx

```json
"mcpServers": {
  "scrape": {
    "command": "uvx",
    "args": ["scraperapi-mcp-server"],
    "env": {
      "API_KEY": "<YOUR_SCRAPERAPI_API_KEY>"
    }
  }
}
```

#### Using docker

```json
"mcpServers": {
  "scrape": {
    "command": "docker",
    "args": ["run", "-i", "--rm", "scraperapi-mcp-server"],
    "env": {
      "API_KEY": "<YOUR_SCRAPERAPI_API_KEY>"
    }
  }
}
```
#### Using pip installation

```json
"mcpServers": {
  "scrape": {
    "command": "python",
    "args": ["-m", "scraperapi_mcp_server"],
    "env": {
      "API_KEY": "<YOUR_SCRAPERAPI_API_KEY>"
    }
  }
}
```

### Configure for VS Code

For manual installation, add the following JSON block to your User Settings (JSON) file in VS Code. You can do this by pressing `Ctrl + Shift + P` and typing `Preferences: Open User Settings (JSON)`.

Optionally, you can add it to a file called `.vscode/mcp.json` in your workspace. This will allow you to share the configuration with others.

> Note that the `mcp` key is needed when using the `mcp.json` file.

#### Using uvx

```json
{
  "mcp": {
    "servers": {
      "scrape": {
        "command": "uvx",
        "args": ["scraperapi_mcp_server"],
        "env": {
          "API_KEY": "<YOUR_SCRAPERAPI_API_KEY>"
        }
      }
    }
  }
}
```
#### Using Docker

```json
{
  "mcp": {
    "servers": {
      "scrape": {
        "command": "docker",
        "args": ["run", "-i", "--rm", "scraperapi-mcp-server"],
        "env": {
          "API_KEY": "<YOUR_SCRAPERAPI_API_KEY>"
        }
      }
    }
  }
}
```

## API Reference

### Available Tools

- `scrape` - Scrape a URL from the internet using ScraperAPI
  - Parameters:
    - `api_key` (string, required): your API key
    - `url` (string, required): URL to scrape
    - `render` (boolean, optional): Render JavaScript on the page
    - `country_code` (string, optional): Activate country geotargeting (ISO 2-letter code)
    - `premium` (boolean, optional): Activate premium residential and mobile IPs
    - `ultra_premium` (boolean, optional): Activate advanced bypass mechanisms. Can not combine with `premium`
    - `device_type` (string, optional): Set request to use 'mobile' or 'desktop' user agents

### Prompts

- **scrape**
  - Scrapes a URL from the internet using ScraperAPI
  - Arguments:
    - `url` (string, required): URL to scrape

## Development

### Local Development

```bash
python3 -m scraperapi_mcp_server.main --debug
```