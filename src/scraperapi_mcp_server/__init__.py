#!/usr/bin/env python3
import sys
from scraperapi_mcp_server.server import mcp

__version__ = "0.1.0" 

def main():
    """ScraperAPI MCP server main module."""
    # Run the server
    mcp.run()
    print('...', file=sys.stderr)   

if __name__ == "__main__":
    main()
