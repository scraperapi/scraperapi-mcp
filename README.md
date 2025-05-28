# ScraperAPI MCP server

The ScraperAPI MCP server enables LLM clients to retrieve and process web scraping requests using the ScraperAPI services.

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

The ScraperAPI MCP Server is designed to run as a local server on your machine.

### Prerequisites
- Python 3.11+
- Docker (optional)

### Using Python

Add this to your client configuration file:

```json
{
  "mcpServers": {
    "ScraperAPI": {
      "command": "<YOUR_COMMAND_PATH>/python",
      "args": ["-m", "scraperapi_mcp_server"],
      "env": {
        "API_KEY": "<YOUR_SCRAPERAPI_API_KEY>"
      }
    }
  }
}
```

### Using Docker 

Add this to your client configuration file:

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
        "scraperapi-mcp-server"]
    }
  }
}
```

</br>

> [!TIP]
>
> When specifying `<YOUR_COMMAND_PATH>`, you must use the path to the command inside your virtual environment. 
>
> To find the correct path activate your virtual environment first then run:
>    ```bash
>    which <YOUR_COMMAND>
>    ```
> Using the wrong path is a common cause of `package not found` errors when clients try to start the server.

## API Reference

### Available Tools

- `scrape`
  - Scrape a URL from the internet using ScraperAPI
  - Parameters:
    - `url` (string, required): URL to scrape
    - `render` (boolean, optional): Whether to render the page using JavaScript. Defaults to `False`. Set to `True` only if the page requires JavaScript rendering to display its content.
    - `country_code` (string, optional): Activate country geotargeting (ISO 2-letter code)
    - `premium` (boolean, optional): Activate premium residential and mobile IPs
    - `ultra_premium` (boolean, optional): Activate advanced bypass mechanisms. Can not combine with `premium`
    - `device_type` (string, optional): Set request to use `mobile` or `desktop` user agents
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
5. Click on "Edit Config" and paste [the JSON configuration file](#installation).

## Development

### Local setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/scraperapi/scraperapi-mcp
   cd scraperapi-mcp
   ```

2. **Install dependencies and run the package locally:**
   - **Using Python:**
     ```bash
     # Create virtual environment and activate it
     python -m venv .venv
     source .venv/bin/activate # MacOS/Linux
     # OR
     .venv/Scripts/activate # Windows

     # Install the local package in editable mode
     pip install -e .
     ```

   - **Using Docker:**
     ```bash
     # Build the Docker image locally
     docker build -t scraperapi-mcp-server .
     ```

### Run the server
   - **Using Python:**
     ```bash
     python -m scraperapi_mcp_server
     ```

   - **Using Docker:**
     ```bash
     # Run the Docker container with your API key
     docker run -e API_KEY=<YOUR_SCRAPERAPI_API_KEY> scraperapi-mcp-server
     ```

### Debug

```bash
python3 -m scraperapi_mcp_server --debug
```