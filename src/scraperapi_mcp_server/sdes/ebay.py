"""eBay structured-data endpoint (SDE) tools.

Each tool wraps a ``GET {API_URL}/structured/ebay/<type>`` endpoint that returns
pre-parsed eBay data as JSON (or CSV).
"""

from typing import Annotated, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from scraperapi_mcp_server.execution import run_sde
from scraperapi_mcp_server.sdes.base import SDE_TOOL_ANNOTATIONS, BaseSdeParams


class EbaySearchParams(BaseSdeParams):
    query: Annotated[
        str,
        Field(
            description="The search keywords, as typed into eBay's search bar (e.g. 'vintage camera'). Required.",
        ),
    ]
    page: Annotated[
        Optional[int],
        Field(
            default=None,
            gt=0,
            description="1-based results page number to retrieve. If omitted, the first page is returned.",
        ),
    ]
    items_per_page: Annotated[
        Optional[int],
        Field(
            default=None,
            gt=0,
            description="Number of items to return per page.",
        ),
    ]
    seller_id: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Restrict results to a specific eBay seller by their seller ID/username.",
        ),
    ]
    condition: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Comma-separated item condition filters: 'new', 'used', 'open_box', 'refurbished', 'for_parts', 'not_working'.",
        ),
    ]
    buying_format: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Buying format filter: 'buy_it_now', 'auction', or 'accepts_offers'.",
        ),
    ]
    show_only: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Comma-separated additional filters: 'returns_accepted', 'authorized_seller', 'completed_items', 'sold_items', 'sale_items', 'listed_as_lots', 'search_in_description', 'benefits_charity', 'authenticity_guarantee'.",
        ),
    ]
    sort_by: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Sort order: 'best_match', 'ending_soonest', 'newly_listed', 'price_lowest', 'price_highest', or 'distance_nearest'.",
        ),
    ]


class EbayProductParams(BaseSdeParams):
    product_id: Annotated[
        str,
        Field(
            description="The eBay item ID (the numeric ID in a listing URL, e.g. '123456789012'). Required.",
        ),
    ]


def register_ebay_tools(mcp: FastMCP) -> None:
    """Register all eBay structured-data tools on the given MCP server."""

    @mcp.tool(name="ebay_search", annotations=SDE_TOOL_ANNOTATIONS)
    async def ebay_search(params: EbaySearchParams) -> str:
        """Retrieve parsed eBay search results for a query.

        Returns structured listing results — title, price, condition, seller, bids,
        shipping, item ID, URL — for a keyword search on eBay, with pagination and
        filtering by condition, buying format, seller, and sort order.

        When to use:
        - Discovering listings and their item IDs for a search term
        - Price/market research, auction monitoring, seller analysis

        When NOT to use:
        - You already have an item ID (use 'ebay_product')

        Args:
            params (EbaySearchParams): query (required) plus optional page,
                items_per_page, seller_id, condition, buying_format, show_only,
                sort_by, tld, country_code, and output_format.

        Returns:
            str: JSON (default) or CSV containing the structured search results.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_sde("/structured/ebay/search", params)

    @mcp.tool(name="ebay_product", annotations=SDE_TOOL_ANNOTATIONS)
    async def ebay_product(params: EbayProductParams) -> str:
        """Retrieve parsed details for a single eBay listing by item ID.

        Returns structured listing data — title, price, condition, seller info,
        description, shipping, and item specifics — for one eBay item.

        When to use:
        - You have an eBay item ID and want its full structured details
        - Listing monitoring, price/spec extraction

        When NOT to use:
        - You only have search keywords (use 'ebay_search' first)

        Args:
            params (EbayProductParams): product_id (required) plus optional tld,
                country_code, and output_format.

        Returns:
            str: JSON (default) or CSV containing the structured listing data.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_sde("/structured/ebay/product", params)
