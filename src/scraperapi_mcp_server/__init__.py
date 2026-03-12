#!/usr/bin/env python3
import logging
from scraperapi_mcp_server.server import mcp

__version__ = "0.2.0"


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
