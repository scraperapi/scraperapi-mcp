# ScraperAPI MCP server

The ScraperAPI MCP server enables LLM clients to retrieve and process web scraping requests using the ScraperAPI services.

[![scraperapi-mcp-server MCP server](https://glama.ai/mcp/servers/scraperapi/scraperapi-mcp/badges/card.svg)](https://glama.ai/mcp/servers/scraperapi/scraperapi-mcp)

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [API Reference](#api-reference)
- [Configuration](#configuration)
  - [Claude Desktop App & Claude Code](#configure-claude-desktop-app--claude-code)
  - [Cursor](#configure-cursor-editor)
  - [Windsurf](#configure-windsurf-editor)
  - [Cline](#configure-cline-vs-code-extension)
- [Development](#development)

## Features

- Full implementation of the Model Context Protocol specification
- Seamless integration with ScraperAPI for web scraping
- Simple setup with Python or Docker

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

The ScraperAPI MCP Server is designed to run as a local server on your machine, your LLM client will launch it automatically when configured.

### Prerequisites
- Python 3.11+
- Docker (optional)

### Using Python

Install the package:
```bash
pip install scraperapi-mcp-server
```

Add this to your client configuration file:

```json
{
  "mcpServers": {
    "ScraperAPI": {
      "command": "python",
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
      "command": "docker",
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
> If your command is not working (for example, you see a `package not found` error when trying to start the server), double-check the path you are using. To find the correct path, activate your virtual environment first, then run:
>    ```bash
>    which <YOUR_COMMAND>
>    ```

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
    - `output_format` (string, optional): Allows you to instruct the API on what the response file type should be.
    - `autoparse` (boolean, optional): Activate auto parsing for select websites. Defaults to `False`. Set to `True` only if you want the output format in `csv` or `json`.
  - Returns: The scraped content as a string

### Prompt templates

- Please scrape this URL `<URL>`. If you receive a 500 server error identify the website's geo-targeting and add the corresponding country_code to overcome geo-restrictions. If errors continues, upgrade the request to use premium proxies by adding premium=true. For persistent failures, activate ultra_premium=true to use enhanced anti-blocking measures.
- Can you scrape URL `<URL>` to extract `<SPECIFIC_DATA>`? If the request returns missing/incomplete`<SPECIFIC_DATA>`, set render=true to enable JS Rendering.

## Configuration

### Settings

- `API_KEY`: Your ScraperAPI API key.

### Configure Claude Desktop App & Claude Code

**Claude Desktop:**
1. Open Claude Desktop and click the settings icon
2. Select the "Developer" tab
3. Click "Edit Config" and paste [the JSON configuration file](#installation)

**Claude Code:**
1. Add the server manually to your `.claude/settings.json` with [the JSON configuration file](#installation), or run:
   ```bash
   claude mcp add scraperapi -e API_KEY=<YOUR_SCRAPERAPI_API_KEY> -- python -m scraperapi_mcp_server
   ```

### Configure Cursor Editor

1. Open Cursor
2. Access the Settings Menu
3. Open Cursor Settings 
4. Go to Tools & Integrations section
5. Click '+ Add MCP Server'
6. Choose Manual and paste [the JSON configuration file](#installation)

More [here](https://cursor.com/docs/context/mcp#servers)

### Configure Windsurf Editor

1. Open Windsurf
2. Access the Settings Menu
3. Click on the Cascade settings
4. Click on the MCP server section
5. Click on the gear icon, the `mcp_config.json` file will open
6. Paste [the JSON configuration file](#installation)

More [here](https://docs.windsurf.com/windsurf/cascade/mcp#adding-a-new-mcp)

### Configure Cline (VS code extension)

1. Open VS Code and click the Cline icon in the activity bar to open the Cline panel
2. Click the MCP Servers icon in the top navigation bar of the Cline pane
3. Select the "Configure" tab
4. Click "Configure MCP Servers" at the bottom of the pane — this opens `cline_mcp_settings.json`
5. Paste [the JSON configuration file](#installation)

More [here](https://docs.cline.bot/mcp/adding-and-configuring-servers#editing-configuration-files)

## Development

### Local setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/scraperapi/scraperapi-mcp
   cd scraperapi-mcp
   ```

2. **Install dependencies:**
   - **Using Poetry:**
     ```bash
     poetry install
     ```
   - **Using pip:**
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

### Testing

This project uses [pytest](https://docs.pytest.org/en/stable/) for testing.

#### Install Test Dependencies
- **Using Poetry:**
  ```bash
  poetry install --with dev
  ```
- **Using pip:**
  ```bash
  pip install -e .
  pip install pytest pytest-mock pytest-asyncio
  ```

#### Running Tests

```bash
# Run All Tests
pytest

# Run Specific Test
pytest <TEST_FILE_PATH>
```