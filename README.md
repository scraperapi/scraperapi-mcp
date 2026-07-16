# ScraperAPI MCP server

The ScraperAPI MCP server enables LLM clients to retrieve and process web scraping requests using the ScraperAPI services.

This is the self-hosted (local) server. A [hosted (remote) version](https://docs.scraperapi.com/integrations/llm-integrations/mcp-server/hosted-remote) is also available.

<div align="center">

[![pypi package](https://img.shields.io/pypi/v/scraperapi-mcp-server?color=%2334D058&label=pypi%20package)](https://pypi.org/project/scraperapi-mcp-server/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

<br/>

[![scraperapi-mcp-server MCP server](https://glama.ai/mcp/servers/scraperapi/scraperapi-mcp/badges/card.svg)](https://glama.ai/mcp/servers/scraperapi/scraperapi-mcp)

</div>

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [API Reference](#api-reference)
- [Configuration](#configuration)
  - [Settings](#settings)
  - [Client Setup](#client-setup)
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

## Available tools

### API

Structured Data Endpoints (SDEs) return pre-parsed JSON (or CSV) instead of raw HTML. Every SDE tool also accepts `output_format` (`json` by default, or `csv`), `tld`, and `country_code`, shown in each tool's table.

<details>
<summary><strong>scrape</strong> — Scrape any web page or image, bypassing anti-bot protection</summary>

Retrieve the content of a web page, or download an image, from a URL.

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `url` | string | Target URL to scrape | Yes |
| `render` | boolean | Enable JavaScript rendering for dynamic pages (default: `false`) | No |
| `country_code` | string | ISO 2-letter country code for geo-targeting | No |
| `premium` | boolean | Use premium residential/mobile proxies (default: `false`) | No |
| `ultra_premium` | boolean | Advanced anti-bot bypass; incompatible with `premium` (default: `false`) | No |
| `device_type` | string | `mobile` or `desktop` user agent | No |
| `output_format` | string | `markdown` (default), `text`, `csv`, or `json` | No |
| `autoparse` | boolean | Auto-parse supported sites into structured data (default: `false`) | No |

Returns: the scraped content as a string, or image data for image URLs.

</details>

### SDEs

#### Google

<details>
<summary><strong>google_search</strong> — Parsed Google Search (SERP) results</summary>

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `query` | string | Search query, as typed into Google | Yes |
| `num` | integer | Number of results to return on the page | No |
| `start` | integer | Zero-based result offset for pagination | No |
| `hl` | string | Interface/host language code (e.g. `en`, `es`) | No |
| `gl` | string | Country edition to search (2-letter code) | No |
| `uule` | string | Google `uule` geolocation string (advanced) | No |
| `date_range_start` | string | Start of a custom date range, `MM/DD/YYYY` | No |
| `date_range_end` | string | End of a custom date range, `MM/DD/YYYY` | No |
| `time_period` | string | Recent window: `1H`, `1D`, `1W`, `1M`, or `1Y` | No |
| `include_html` | boolean | Include raw HTML alongside parsed data (default: `false`) | No |
| `tbs` | string | Raw Google `tbs` filter parameter (advanced) | No |
| `output_format` | string | `json` (default) or `csv` | No |
| `tld` | string | Top-level domain (e.g. `com`, `co.uk`) | No |
| `country_code` | string | ISO 2-letter country code for geo-targeting | No |

</details>

<details>
<summary><strong>google_news</strong> — Parsed Google News results</summary>

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `query` | string | Search query | Yes |
| `num` | integer | Number of results to return on the page | No |
| `start` | integer | Zero-based result offset for pagination | No |
| `hl` | string | Interface/host language code | No |
| `gl` | string | Country edition to search (2-letter code) | No |
| `uule` | string | Google `uule` geolocation string (advanced) | No |
| `date_range_start` | string | Start of a custom date range, `MM/DD/YYYY` | No |
| `date_range_end` | string | End of a custom date range, `MM/DD/YYYY` | No |
| `time_period` | string | Recent window: `1H`, `1D`, `1W`, `1M`, or `1Y` | No |
| `output_format` | string | `json` (default) or `csv` | No |
| `tld` | string | Top-level domain (e.g. `com`, `co.uk`) | No |
| `country_code` | string | ISO 2-letter country code for geo-targeting | No |

</details>

<details>
<summary><strong>google_jobs</strong> — Parsed Google Jobs listings</summary>

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `query` | string | Search query | Yes |
| `num` | integer | Number of results to return on the page | No |
| `start` | integer | Zero-based result offset for pagination | No |
| `hl` | string | Interface/host language code | No |
| `gl` | string | Country edition to search (2-letter code) | No |
| `uule` | string | Google `uule` geolocation string (advanced) | No |
| `output_format` | string | `json` (default) or `csv` | No |
| `tld` | string | Top-level domain (e.g. `com`, `co.uk`) | No |
| `country_code` | string | ISO 2-letter country code for geo-targeting | No |

</details>

<details>
<summary><strong>google_shopping</strong> — Parsed Google Shopping product results</summary>

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `query` | string | Search query | Yes |
| `num` | integer | Number of results to return on the page | No |
| `start` | integer | Zero-based result offset for pagination | No |
| `hl` | string | Interface/host language code | No |
| `gl` | string | Country edition to search (2-letter code) | No |
| `uule` | string | Google `uule` geolocation string (advanced) | No |
| `include_html` | boolean | Include raw HTML alongside parsed data (default: `false`) | No |
| `output_format` | string | `json` (default) or `csv` | No |
| `tld` | string | Top-level domain (e.g. `com`, `co.uk`) | No |
| `country_code` | string | ISO 2-letter country code for geo-targeting | No |

</details>

<details>
<summary><strong>google_maps_search</strong> — Parsed Google Maps place/business results</summary>

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `query` | string | Search query (e.g. `coffee shops in Austin`) | Yes |
| `latitude` | number | Latitude of the map center, in decimal degrees | No |
| `longitude` | number | Longitude of the map center, in decimal degrees | No |
| `zoom` | integer | Map zoom level (roughly 3=country, 10=city, 15=street) | No |
| `include_html` | boolean | Include raw HTML alongside parsed data (default: `false`) | No |
| `output_format` | string | `json` (default) or `csv` | No |
| `tld` | string | Top-level domain (e.g. `com`, `co.uk`) | No |
| `country_code` | string | ISO 2-letter country code for geo-targeting | No |

</details>

#### Amazon

<details>
<summary><strong>amazon_product</strong> — Parsed Amazon product details by ASIN</summary>

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `asin` | string | 10-character Amazon product identifier (e.g. `B08N5WRWNW`) | Yes |
| `language` | string | Language code for localized content (e.g. `en_US`) | No |
| `include_html` | boolean | Include raw HTML alongside parsed data (default: `false`) | No |
| `output_format` | string | `json` (default) or `csv` | No |
| `tld` | string | Amazon TLD (e.g. `com`, `co.uk`, `de`) | No |
| `country_code` | string | ISO 2-letter country code for geo-targeting | No |

</details>

<details>
<summary><strong>amazon_search</strong> — Parsed Amazon product search results</summary>

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `query` | string | Search query, as typed into Amazon | Yes |
| `page` | integer | 1-based results page number | No |
| `sort_by` | string | Sort order (e.g. `price-asc-rank`, `review-rank`) | No |
| `department` | string | Restrict search to a department/category (e.g. `electronics`) | No |
| `ref` | string | Amazon `ref` referral/context token (advanced) | No |
| `language` | string | Language code for localized content | No |
| `output_format` | string | `json` (default) or `csv` | No |
| `tld` | string | Amazon TLD (e.g. `com`, `co.uk`, `de`) | No |
| `country_code` | string | ISO 2-letter country code for geo-targeting | No |

</details>

<details>
<summary><strong>amazon_offers</strong> — Parsed seller offers for an Amazon product</summary>

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `asin` | string | 10-character Amazon product identifier | Yes |
| `condition` | string | Comma-separated condition filters (e.g. `f_new,f_usedLikeNew`) | No |
| `f_new` | boolean | Include only New-condition offers | No |
| `f_used_like_new` | boolean | Include Used - Like New offers | No |
| `f_used_very_good` | boolean | Include Used - Very Good offers | No |
| `f_used_good` | boolean | Include Used - Good offers | No |
| `f_used_acceptable` | boolean | Include Used - Acceptable offers | No |
| `language` | string | Language code for localized content | No |
| `output_format` | string | `json` (default) or `csv` | No |
| `tld` | string | Amazon TLD (e.g. `com`, `co.uk`, `de`) | No |
| `country_code` | string | ISO 2-letter country code for geo-targeting | No |

</details>

### Prompt templates

- Please scrape this URL `<URL>`. If you receive a 500 server error identify the website's geo-targeting and add the corresponding country_code to overcome geo-restrictions. If errors continues, upgrade the request to use premium proxies by adding premium=true. For persistent failures, activate ultra_premium=true to use enhanced anti-blocking measures.
- Can you scrape URL `<URL>` to extract `<SPECIFIC_DATA>`? If the request returns missing/incomplete`<SPECIFIC_DATA>`, set render=true to enable JS Rendering.

## Configuration

### Settings

Configure the server through environment variables. Only `API_KEY` is required.

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEY` | — | **Required.** Your ScraperAPI API key. |
| `API_URL` | `https://api.scraperapi.com` | Base URL for the ScraperAPI API and structured-data endpoints. Override to target staging. |
| `SCRAPER_SDK` | `mcp-server` | Client identifier sent to ScraperAPI on every request. |
| `API_TIMEOUT_SECONDS` | `70` | Per-request timeout, in seconds. |
| `RATE_LIMIT_MAX_CALLS` | `10` | Maximum tool calls allowed per rate-limit window. |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | Length of the rate-limit window, in seconds. |
| `IMAGE_SIZE_LIMIT_BYTES` | `700000` | Maximum size of an image the `scrape` tool returns inline. |

### Client Setup

Use [the JSON configuration file](#installation) from the Installation section. Below are steps for common clients.

<details>
<summary><strong>Claude Desktop & Claude Code</strong></summary>

**Claude Desktop:**
1. Open Claude Desktop and click the settings icon
2. Select the "Developer" tab
3. Click "Edit Config" and paste [the JSON configuration file](#installation)

**Claude Code:**
1. Add the server manually to your `.claude/settings.json` with [the JSON configuration file](#installation), or run:
   ```bash
   claude mcp add scraperapi -e API_KEY=<YOUR_SCRAPERAPI_API_KEY> -- python -m scraperapi_mcp_server
   ```

</details>

<details>
<summary><strong>Cursor Editor</strong></summary>

1. Open Cursor
2. Access the Settings Menu
3. Open Cursor Settings
4. Go to Tools & Integrations section
5. Click '+ Add MCP Server'
6. Choose Manual and paste [the JSON configuration file](#installation)

More [here](https://cursor.com/docs/context/mcp#servers)

</details>

<details>
<summary><strong>Windsurf Editor</strong></summary>

1. Open Windsurf
2. Access the Settings Menu
3. Click on the Cascade settings
4. Click on the MCP server section
5. Click on the gear icon, the `mcp_config.json` file will open
6. Paste [the JSON configuration file](#installation)

More [here](https://docs.windsurf.com/windsurf/cascade/mcp#adding-a-new-mcp)

</details>

<details>
<summary><strong>Cline (VS Code extension)</strong></summary>

1. Open VS Code and click the Cline icon in the activity bar to open the Cline panel
2. Click the MCP Servers icon in the top navigation bar of the Cline pane
3. Select the "Configure" tab
4. Click "Configure MCP Servers" at the bottom of the pane — this opens `cline_mcp_settings.json`
5. Paste [the JSON configuration file](#installation)

More [here](https://docs.cline.bot/mcp/adding-and-configuring-servers#editing-configuration-files)

</details>

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