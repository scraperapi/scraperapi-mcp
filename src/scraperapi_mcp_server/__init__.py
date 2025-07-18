#!/usr/bin/env python3
import logging
from scraperapi_mcp_server.server import mcp

__version__ = "0.1.0"


def main():
    """ScraperAPI MCP server main module."""
    logging.info("Starting ScraperAPI MCP server main module.")
    # Run the server
    try:
        logging.debug("Running ScraperAPI MCP server...")
        mcp.run()
    except Exception as e:
        logging.exception(
            f"Unhandled exception in ScraperAPI MCP server main loop: {e}"
        )
        raise


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    main()
