from mcp.server.fastmcp import FastMCP

from scraperapi_mcp_server.scrape.scrape import register_scrape_tool
from scraperapi_mcp_server.sdes.google import register_google_tools
from scraperapi_mcp_server.sdes.amazon import register_amazon_tools
from scraperapi_mcp_server.sdes.walmart import register_walmart_tools
from scraperapi_mcp_server.sdes.ebay import register_ebay_tools
from scraperapi_mcp_server.sdes.redfin import register_redfin_tools
from scraperapi_mcp_server.crawler.crawler import register_crawler_tools
from scraperapi_mcp_server.aiparser.aiparser import register_aiparser_tools

mcp = FastMCP("ScraperAPI")

register_scrape_tool(mcp)
register_google_tools(mcp)
register_amazon_tools(mcp)
register_walmart_tools(mcp)
register_ebay_tools(mcp)
register_redfin_tools(mcp)
register_crawler_tools(mcp)
register_aiparser_tools(mcp)
