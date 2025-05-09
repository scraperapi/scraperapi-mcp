# ScraperAPI MCP server

The ScraperAPI MCP server enables LLMs to retrieve and process web scraping requests using the ScraperAPI service.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [API Reference](#api-reference)
- [Configuration](#configuration)
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

### Clone the repository:
  ```bash
  git clone https://github.com/scraperapi/scraperapi-mcp
  cd scraperapi-mcp
  ```

### Using Python

- With `uv` (recommended)
  ```bash
  # Create virtual environment and activate it
  uv venv

  source .venv/bin/activate # MacOS/Linux
  # OR
  .venv/Scripts/activate # Windows

  # Install dependencies 
  uv sync

  uvx scraperapi-mcp-server
  ```

- With `pip`
  ```bash
  # Create virtual environment and activate it
  python -m venv myenv

  source .venv/bin/activate # MacOS/Linux
  # OR
  .venv/Scripts/activate # Windows

  pip install scraperapi_mcp_server

  python -m scraperapi_mcp_server
  ```

### Using Docker

You can build and run the MCP server using Docker:

```bash
# Build the Docker image
docker build -t scraperapi-mcp-server .

# Run the Docker container with environment variable
docker run -e API_KEY=<YOUR_SCRAPERAPI_API_KEY> scraperapi-mcp-server
```

## API Reference

### Available Tools

- `scrape`
  - Scrape a URL from the internet using ScraperAPI
  - Parameters:
    - `api_key` (string, required): your API key
    - `url` (string, required): URL to scrape
    - `render` (boolean, optional): Whether to render the page using JavaScript. Defaults to `False`. Set to `True` only if the page requires JavaScript rendering to display its content.
    - `country_code` (string, optional): Activate country geotargeting (ISO 2-letter code)
    - `premium` (boolean, optional): Activate premium residential and mobile IPs
    - `ultra_premium` (boolean, optional): Activate advanced bypass mechanisms. Can not combine with `premium`
    - `device_type` (string, optional): Set request to use `mobile` or `desktop` user agents
  - Returns: The scraped content as a string

- `scrape_assisted`
  - Scrape a URL using ScraperAPI with smart scraping logic
  - **Note: This tool can lead to increased costs** as it may use premium features to ensure successful scraping
  - Parameters:
    - `url` (string, required): URL to scrape
    - `device_type` (string, optional): Set to "mobile" or "desktop" to use specific user agents
    - `country_code` (string, optional): Two-letter country code to scrape from
  - Returns: The scraped content as a string

### Example Queries

Here are some example queries demonstrating different use cases:

- Scrape https://example.com
- Scrape https://example.com from Germany
- Could you scrape https://example.com with JavaScript rendering from a mobile device in France using premium scraping?
- Use the smart scraping logic to scrape https://example.com as it's a complex website with anti-bot measures

## Configuration

### Settings

- `API_KEY`: Your ScraperAPI API key.

### Configure for Claude Desktop App

1. Open Claude Desktop Application
2. Access the Settings Menu
3. Click on the settings icon (typically a gear or three dots in the upper right corner)
4. Select the "Developer" tab
5. Click on "Edit Config" and paste [the JSON configuration file](#json-configuration-file).

### JSON configuration file.

<details>
<summary>Using uvx</summary>

```json
"mcpServers": {
  "ScraperAPI": {
    "command": "<YOUR_COMMAND_PATH>/uvx",
    "args": ["scraperapi-mcp-server"],
    "env": {
      "API_KEY": "<YOUR_SCRAPERAPI_API_KEY>"
    }
  }
}
```

</details>

<details>
<summary>Using pip installation</summary>

```json
"mcpServers": {
  "ScraperAPI": {
    "command": "<YOUR_COMMAND_PATH>/python",
    "args": ["-m", "scraperapi_mcp_server"],
    "env": {
      "API_KEY": "<YOUR_SCRAPERAPI_API_KEY>"
    }
  }
}
```

</details>

<details>
<summary>Using docker</summary>

```json
{
  "mcpServers": {
    "ScraperAPI": {
      "command": "<YOUR_COMMAND_PATH>/docker",
      "args": [
        "run",
        "-i",
        "-e",
        "API_KEY=${API_KEY}",
        "--rm",
        "scraperapi-mcp-server"],
      "env": {
        "API_KEY": "<YOUR_SCRAPERAPI_API_KEY>"
      }
    }
  }
}
```
</details>

> If you don't know what `<YOUR_COMMAND_PATH>` is, you can type `which <YOUR_COMMAND>` on a terminal to find out.

## Development

### Local Development

```bash
python3 -m scraperapi_mcp_server --debug
```