"""Amazon structured-data endpoint (SDE) tools.

Each tool wraps a ``GET {API_URL}/structured/amazon/<type>`` endpoint that
returns pre-parsed Amazon data as JSON (or CSV).
"""

from typing import Annotated, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from scraperapi_mcp_server.execution import run_sde
from scraperapi_mcp_server.sdes.base import SDE_TOOL_ANNOTATIONS, BaseSdeParams

# ASINs are Amazon's 10-character alphanumeric product identifiers.
_ASIN_PATTERN = r"^[A-Za-z0-9]{10}$"


class _AmazonBaseParams(BaseSdeParams):
    """Shared optional params for every Amazon endpoint."""

    language: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Language code for localized content (e.g. 'en_US', 'de_DE'). Controls the language Amazon renders the listing in.",
        ),
    ]


class AmazonProductParams(_AmazonBaseParams):
    asin: Annotated[
        str,
        Field(
            pattern=_ASIN_PATTERN,
            description="The 10-character Amazon product identifier (ASIN), e.g. 'B08N5WRWNW'. Required. Find it in the product URL (/dp/<ASIN>).",
        ),
    ]
    include_html: Annotated[
        Optional[bool],
        Field(
            default=None,
            description="When true, include the raw HTML of the product page alongside the parsed data. Increases response size. Default: false.",
        ),
    ]


class AmazonSearchParams(_AmazonBaseParams):
    query: Annotated[
        str,
        Field(
            description="The search query, exactly as a user would type it into Amazon's search bar (e.g. 'kids backpack'). Required.",
        ),
    ]
    page: Annotated[
        Optional[int],
        Field(
            default=None,
            gt=0,
            description="1-based results page number to retrieve (e.g. 1, 2, 3). If omitted, the first page is returned.",
        ),
    ]
    sort_by: Annotated[
        Optional[str],
        Field(
            default=None,
            serialization_alias="s",
            description="Sort order for search results (Amazon's 's' parameter), e.g. 'price-asc-rank', 'review-rank', 'date-desc-rank'.",
        ),
    ]
    department: Annotated[
        Optional[str],
        Field(
            default=None,
            serialization_alias="i",
            description="Restrict the search to an Amazon department/category (Amazon's 'i' parameter), e.g. 'electronics', 'toys-and-games'.",
        ),
    ]
    ref: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Amazon 'ref' referral/context token, occasionally required to reproduce a specific results view. Advanced use.",
        ),
    ]


class AmazonOffersParams(_AmazonBaseParams):
    asin: Annotated[
        str,
        Field(
            pattern=_ASIN_PATTERN,
            description="The 10-character Amazon product identifier (ASIN) to list offers for, e.g. 'B08N5WRWNW'. Required.",
        ),
    ]
    condition: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Comma-separated condition filters as an alternative to the individual f_* flags (e.g. 'f_new,f_usedlikenew,f_usedverygood,f_usedgood,f_usedacceptable'). Limits offers to the given conditions.",
        ),
    ]
    f_new: Annotated[
        Optional[bool],
        Field(
            default=None,
            description="When true, include only New-condition offers.",
        ),
    ]
    f_used_like_new: Annotated[
        Optional[bool],
        Field(
            default=None,
            description="When true, include Used - Like New condition offers.",
        ),
    ]
    f_used_very_good: Annotated[
        Optional[bool],
        Field(
            default=None,
            description="When true, include Used - Very Good condition offers.",
        ),
    ]
    f_used_good: Annotated[
        Optional[bool],
        Field(
            default=None,
            description="When true, include Used - Good condition offers.",
        ),
    ]
    f_used_acceptable: Annotated[
        Optional[bool],
        Field(
            default=None,
            description="When true, include Used - Acceptable condition offers.",
        ),
    ]


def register_amazon_tools(mcp: FastMCP) -> None:
    """Register all Amazon structured-data tools on the given MCP server."""

    @mcp.tool(name="amazon_product", annotations=SDE_TOOL_ANNOTATIONS)
    async def amazon_product(params: AmazonProductParams) -> str:
        """Retrieve parsed details for a single Amazon product by ASIN.

        Returns structured product data — name, brand, pricing, images, feature
        bullets, product information, review summary, category, coupon flags — for
        one Amazon listing, already parsed from the product page.

        When to use:
        - You have a specific ASIN and want its full structured details
        - Product monitoring, catalog enrichment, price/spec extraction

        When NOT to use:
        - You only have a search term, not an ASIN (use 'amazon_search' first)
        - You need the list of sellers/offers for the product (use 'amazon_offers')

        Args:
            params (AmazonProductParams): asin (required) plus optional tld,
                country_code, language, output_format, and include_html.

        Returns:
            str: JSON (default) or CSV containing the structured product data.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_sde("/structured/amazon/product", params)

    @mcp.tool(name="amazon_search", annotations=SDE_TOOL_ANNOTATIONS)
    async def amazon_search(params: AmazonSearchParams) -> str:
        """Retrieve parsed Amazon search results for a query.

        Returns structured search results — product name, price, rating, review
        count, URL, image, Prime/best-seller/sponsored flags — plus pagination,
        for a keyword search on Amazon.

        When to use:
        - Discovering products and their ASINs for a search term
        - Price/market research and catalog building across a category

        When NOT to use:
        - You already have an ASIN (use 'amazon_product' / 'amazon_offers')

        Args:
            params (AmazonSearchParams): query (required) plus optional page,
                sort_by, department, ref, tld, country_code, language, and
                output_format.

        Returns:
            str: JSON (default) or CSV containing the structured search results.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_sde("/structured/amazon/search", params)

    @mcp.tool(name="amazon_offers", annotations=SDE_TOOL_ANNOTATIONS)
    async def amazon_offers(params: AmazonOffersParams) -> str:
        """Retrieve the parsed list of seller offers for an Amazon product.

        Returns structured offer listings for one ASIN — listing/shipping price,
        condition, seller name and rating, Prime/FBA flags, and delivery info —
        across the sellers offering that product.

        When to use:
        - Comparing sellers, prices, and conditions (new/used) for a known ASIN
        - Buy-box / third-party seller and repricing analysis

        When NOT to use:
        - You want the product's own details (use 'amazon_product')
        - You only have a search term (use 'amazon_search' to get the ASIN first)

        Args:
            params (AmazonOffersParams): asin (required) plus optional condition
                filters (condition, f_new, f_used_like_new, f_used_very_good,
                f_used_good, f_used_acceptable), tld, country_code, language, and
                output_format.

        Returns:
            str: JSON (default) or CSV containing the structured offers.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_sde("/structured/amazon/offers", params)
