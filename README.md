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

The ScraperAPI MCP Server is designed to run as a local server on your machine, your LLM client will launch it automatically when configured.

### Prerequisites
- Python 3.11+

### Using Python

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
  - Returns: The scraped content as a string

### Prompt templates

- Please scrape this URL `<URL>`. If you receive a 500 server error identify the website's geo-targeting and add the corresponding country_code to overcome geo-restrictions. If errors continues, upgrade the request to use premium proxies by adding premium=true. For persistent failures, activate ultra_premium=true to use enhanced anti-blocking measures.
- Can you scrape URL `<URL>` to extract `<SPECIFIC_DATA>`? If the request returns missing/incomplete`<SPECIFIC_DATA>`, set render=true to enable JS Rendering.

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


### Run the server
   - **Using Python:**
     ```bash
     python -m scraperapi_mcp_server
     ```


### Debug

```bash
python3 -m scraperapi_mcp_server --debug
```

### Testing

This project uses [pytest](https://docs.pytest.org/en/stable/) for testing.

#### Install Test Dependencies
```bash
# Install the package with test dependencies
pip install -e ".[test]"
```

#### Running Tests

```bash
# Run All Tests
pytest

# Run Specific Test
pytest <TEST_FILE_PATH>
```