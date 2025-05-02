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
- Simple setup with Python

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

- Python 3.11+

### Setup:

1. Clone the repository
  ```bash
  git clone https://github.com/scraperapi/scraperapi-mcp
  cd scraperapi-mcp
  ```

2. Install and run
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

## API Reference

### Available Tools

- `scrape` - Scrape a URL from the internet using ScraperAPI
  - Parameters:
    - `api_key` (string, required): your API key
    - `url` (string, required): URL to scrape
    - `render` (boolean, optional): Whether to render the page using JavaScript. Defaults to `False`. Set to `True` only if the page requires JavaScript rendering to display its content.
    - `country_code` (string, optional): Activate country geotargeting (ISO 2-letter code)
    - `premium` (boolean, optional): Activate premium residential and mobile IPs
    - `ultra_premium` (boolean, optional): Activate advanced bypass mechanisms. Can not combine with `premium`
    - `device_type` (string, optional): Set request to use `mobile` or `desktop` user agents

### Prompts

- **scrape**
  - Scrapes a URL from the internet using ScraperAPI
  - Supports natural language instructions to configure:
    - `url` (string, required): URL to scrape
    - `render` (boolean, optional): Enable JavaScript rendering by mentioning "javascript" or "render"
    - `device_type` (string, optional): Set to "mobile" or "desktop" by mentioning the device type
    - `premium` (boolean, optional): Enable premium scraping by mentioning "premium"
    - `ultra_premium` (boolean, optional): Enable ultra premium scraping by mentioning "ultra premium"
    - `country_code` (string, optional): Specify a country by name to scrape from that location

### Example Queries

Here are some example queries demonstrating different use cases:

- Scrape https://example.com
- Scrape https://example.com from Germany
- Could you scrape https://example.com with JavaScript rendering from a mobile device in France using premium scraping?

## Configuration

### Settings

- `API_KEY`: Your ScraperAPI API key.
- `API_TIMEOUT_SECONDS`: By default is set to 70 seconds. This is because the API may retry failed requests for up to 70 seconds before returning a 500 error. Setting your timeout to 70 seconds ensures that your request has enough time for all retries to be attempted before timing out.

### Configure for Claude Desktop App

1. Open Claude Desktop Application
2. Access the Settings Menu
3. Click on the settings icon (typically a gear or three dots in the upper right corner)
4. Select the "Developer" tab
5. Click on "Edit Config" and paste [the JSON configuration file](#json-configuration-file).


### Configure for Cursor AI

**Project Configuration**

For tools specific to a project, create a `.cursor/mcp.json` file in your project directory. This allows you to define MCP servers that are only available within that specific project.

**Global Configuration**

For tools that you want to use across all projects, create a `\~/.cursor/mcp.json` file in your home directory. This makes MCP servers available in all your Cursor workspaces.


### JSON configuration file.

<details>
<summary>Using uvx</summary>

```json
"mcpServers": {
  "scrape": {
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
  "scrape": {
    "command": "<YOUR_COMMAND_PATH>/python",
    "args": ["-m", "scraperapi_mcp_server"],
    "env": {
      "API_KEY": "<YOUR_SCRAPERAPI_API_KEY>"
    }
  }
}
```

</details>

Note: if you don't know what `<YOUR_COMMAND_PATH>` is, you can type `which <YOUR_COMMAND>` on a terminal to find out.

## Development

### Local Development

```bash
python3 -m scraperapi_mcp_server --debug
```