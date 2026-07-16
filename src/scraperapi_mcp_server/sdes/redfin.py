"""Redfin structured-data endpoint (SDE) tools.

Each tool wraps a ``GET {API_URL}/structured/redfin/<type>`` endpoint that
returns pre-parsed Redfin real-estate data as JSON (or CSV).
"""

from typing import Annotated, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from scraperapi_mcp_server.execution import run_sde
from scraperapi_mcp_server.sdes.base import SDE_TOOL_ANNOTATIONS, BaseSdeParams


class _RedfinUrlParams(BaseSdeParams):
    """Base for every Redfin endpoint: a full Redfin URL plus the shared SDE params."""

    url: Annotated[
        str,
        Field(
            description="The full Redfin URL to parse (e.g. 'https://www.redfin.com/NY/New-York/970-Park-Ave-10028/unit-5N/home/193335918'). Must match the tool: a property page for for_sale/for_rent, a search-results page for search, or an agent profile page for agent. Required.",
        ),
    ]


_RAW_FIELD = Field(
    default=None,
    description="When true, return the raw extracted JSON instead of the cleaned/parsed structure. Default: false.",
)


class RedfinForSaleParams(_RedfinUrlParams):
    raw: Annotated[Optional[bool], _RAW_FIELD]


class RedfinForRentParams(_RedfinUrlParams):
    raw: Annotated[Optional[bool], _RAW_FIELD]


class RedfinSearchParams(_RedfinUrlParams):
    pass


class RedfinAgentParams(_RedfinUrlParams):
    pass


def register_redfin_tools(mcp: FastMCP) -> None:
    """Register all Redfin structured-data tools on the given MCP server."""

    @mcp.tool(name="redfin_for_sale", annotations=SDE_TOOL_ANNOTATIONS)
    async def redfin_for_sale(params: RedfinForSaleParams) -> str:
        """Retrieve parsed Redfin listing data for a home for sale.

        Returns structured property data — price, beds/baths, square footage,
        address, description, photos, price history, and listing details — from a
        Redfin for-sale property page.

        When to use:
        - Extracting details for a specific for-sale property from its Redfin URL
        - Real-estate data collection, comps, or listing monitoring

        When NOT to use:
        - A rental listing (use 'redfin_for_rent')
        - A search-results page (use 'redfin_search') or agent profile ('redfin_agent')

        Args:
            params (RedfinForSaleParams): url (required, full Redfin property URL)
                plus optional raw, tld, country_code, and output_format.

        Returns:
            str: JSON (default) or CSV containing the structured property data.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_sde("/structured/redfin/forsale", params)

    @mcp.tool(name="redfin_for_rent", annotations=SDE_TOOL_ANNOTATIONS)
    async def redfin_for_rent(params: RedfinForRentParams) -> str:
        """Retrieve parsed Redfin listing data for a rental property.

        Returns structured rental data — rent, beds/baths, square footage, address,
        description, photos, and availability — from a Redfin rental property page.

        When to use:
        - Extracting details for a specific rental from its Redfin URL
        - Rental-market data collection or listing monitoring

        When NOT to use:
        - A for-sale listing (use 'redfin_for_sale')
        - A search-results page (use 'redfin_search') or agent profile ('redfin_agent')

        Args:
            params (RedfinForRentParams): url (required, full Redfin rental URL)
                plus optional raw, tld, country_code, and output_format.

        Returns:
            str: JSON (default) or CSV containing the structured rental data.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_sde("/structured/redfin/forrent", params)

    @mcp.tool(name="redfin_search", annotations=SDE_TOOL_ANNOTATIONS)
    async def redfin_search(params: RedfinSearchParams) -> str:
        """Retrieve parsed Redfin search results for a search-results URL.

        Returns a structured list of properties — address, price, beds/baths,
        square footage, URL — from a Redfin search-results page (with its filters
        encoded in the URL).

        When to use:
        - Collecting listings for an area or filter set from a Redfin search URL
        - Building datasets of properties matching search criteria

        When NOT to use:
        - A single property (use 'redfin_for_sale' / 'redfin_for_rent')

        Args:
            params (RedfinSearchParams): url (required, full Redfin search URL with
                filters) plus optional tld, country_code, and output_format.

        Returns:
            str: JSON (default) or CSV containing the structured search results.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_sde("/structured/redfin/search", params)

    @mcp.tool(name="redfin_agent", annotations=SDE_TOOL_ANNOTATIONS)
    async def redfin_agent(params: RedfinAgentParams) -> str:
        """Retrieve parsed Redfin real-estate agent profile data.

        Returns structured agent data — name, contact, brokerage, ratings, and
        recent transactions/listings — from a Redfin agent profile page.

        When to use:
        - Extracting an agent's profile and activity from their Redfin URL
        - Agent research or lead building

        When NOT to use:
        - Property or search data (use the other Redfin tools)

        Args:
            params (RedfinAgentParams): url (required, full Redfin agent profile
                URL) plus optional tld, country_code, and output_format.

        Returns:
            str: JSON (default) or CSV containing the structured agent data.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_sde("/structured/redfin/agent", params)
