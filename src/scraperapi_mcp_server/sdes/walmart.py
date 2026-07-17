"""Walmart structured-data endpoint (SDE) tools.

Each tool wraps a ``GET {API_URL}/structured/walmart/<type>`` endpoint that
returns pre-parsed Walmart data as JSON (or CSV).
"""

from typing import Annotated, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from scraperapi_mcp_server.execution import run_sde
from scraperapi_mcp_server.sdes.base import SDE_TOOL_ANNOTATIONS, BaseSdeParams

_PAGE_FIELD = Field(
    default=None,
    gt=0,
    description="1-based results page number to retrieve. If omitted, the first page is returned.",
)


class WalmartSearchParams(BaseSdeParams):
    query: Annotated[
        str,
        Field(
            description="The product search query, as typed into Walmart's search bar (e.g. 'kids backpack'). Required.",
        ),
    ]
    page: Annotated[Optional[int], _PAGE_FIELD]


class WalmartProductParams(BaseSdeParams):
    product_id: Annotated[
        str,
        Field(
            description="The Walmart product ID (the numeric ID in a product URL, e.g. '5029197970'). Required.",
        ),
    ]


class WalmartCategoryParams(BaseSdeParams):
    category: Annotated[
        str,
        Field(
            description="The Walmart category ID to browse (e.g. '5438' for Electronics). Required.",
        ),
    ]
    page: Annotated[Optional[int], _PAGE_FIELD]


class WalmartReviewParams(BaseSdeParams):
    product_id: Annotated[
        str,
        Field(
            description="The Walmart product ID to fetch reviews for. Required.",
        ),
    ]
    page: Annotated[Optional[int], _PAGE_FIELD]
    sort: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Sort order for the reviews, e.g. 'helpful' or 'recent'.",
        ),
    ]
    ratings: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Comma-separated star ratings to filter by, e.g. '4,5' to only include 4- and 5-star reviews.",
        ),
    ]
    verified_purchase: Annotated[
        Optional[bool],
        Field(
            default=None,
            description="When true, include only reviews with a Walmart 'Verified Purchase' badge. Default: false.",
        ),
    ]


def register_walmart_tools(mcp: FastMCP) -> None:
    """Register all Walmart structured-data tools on the given MCP server."""

    @mcp.tool(name="walmart_search", annotations=SDE_TOOL_ANNOTATIONS)
    async def walmart_search(params: WalmartSearchParams) -> str:
        """Retrieve parsed Walmart product search results for a query.

        Returns structured search results — product name, price, rating, review
        count, product ID, URL, image — plus pagination, for a keyword search on
        Walmart.

        When to use:
        - Discovering products and their Walmart product IDs for a search term
        - Price/market research and catalog building across a category

        When NOT to use:
        - You already have a product ID (use 'walmart_product' / 'walmart_review')

        Args:
            params (WalmartSearchParams): query (required) plus optional page,
                tld, country_code, and output_format.

        Returns:
            str: JSON (default) or CSV containing the structured search results.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_sde("/structured/walmart/search", params)

    @mcp.tool(name="walmart_product", annotations=SDE_TOOL_ANNOTATIONS)
    async def walmart_product(params: WalmartProductParams) -> str:
        """Retrieve parsed details for a single Walmart product by product ID.

        Returns structured product data — name, brand, pricing, availability,
        specifications, images, and review summary — for one Walmart listing.

        When to use:
        - You have a Walmart product ID and want its full structured details
        - Product monitoring, catalog enrichment, price/spec extraction

        When NOT to use:
        - You only have a search term (use 'walmart_search' first)
        - You want the product's reviews (use 'walmart_review')

        Args:
            params (WalmartProductParams): product_id (required) plus optional
                tld, country_code, and output_format.

        Returns:
            str: JSON (default) or CSV containing the structured product data.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_sde("/structured/walmart/product", params)

    @mcp.tool(name="walmart_category", annotations=SDE_TOOL_ANNOTATIONS)
    async def walmart_category(params: WalmartCategoryParams) -> str:
        """Browse parsed products within a Walmart category by category ID.

        Returns a structured list of products in a Walmart category, with
        pagination.

        When to use:
        - Exploring products within a specific Walmart department/category
        - Building category-level catalogs or monitoring a category

        When NOT to use:
        - Free-text product discovery (use 'walmart_search')

        Args:
            params (WalmartCategoryParams): category (required) plus optional
                page, tld, country_code, and output_format.

        Returns:
            str: JSON (default) or CSV containing the category product list.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_sde("/structured/walmart/category", params)

    @mcp.tool(name="walmart_review", annotations=SDE_TOOL_ANNOTATIONS)
    async def walmart_review(params: WalmartReviewParams) -> str:
        """Retrieve parsed customer reviews for a Walmart product by product ID.

        Returns structured reviews — rating, title, text, author, date, verified
        purchase status — for one Walmart product, with pagination, sorting, and
        rating/verified filters.

        When to use:
        - Sentiment analysis or review mining for a known Walmart product
        - Tracking new reviews or filtering by star rating

        When NOT to use:
        - You want the product's own details (use 'walmart_product')
        - You only have a search term (use 'walmart_search' to get the ID first)

        Args:
            params (WalmartReviewParams): product_id (required) plus optional page,
                sort, ratings, verified_purchase, tld, country_code, and
                output_format.

        Returns:
            str: JSON (default) or CSV containing the structured reviews.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_sde("/structured/walmart/review", params)
