#!/usr/bin/env python3
import logging
from importlib.metadata import PackageNotFoundError, version

from scraperapi_mcp_server.server import mcp

try:
    __version__ = version("scraperapi-mcp-server")
except PackageNotFoundError:  # running from source without an install
    __version__ = "0.0.0"


def main():
    """ScraperAPI MCP server main module."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    logging.info("Starting ScraperAPI MCP server main module.")
    try:
        logging.debug("Running ScraperAPI MCP server...")
        mcp.run()
    except Exception as e:
        logging.exception(
            f"Unhandled exception in ScraperAPI MCP server main loop: {e}"
        )
        raise


if __name__ == "__main__":
    main()
