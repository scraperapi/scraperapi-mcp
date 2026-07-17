"""Google structured-data endpoint (SDE) tools.

Each tool wraps a ``GET {API_URL}/structured/google/<type>`` endpoint that
returns pre-parsed Google results as JSON (or CSV).
"""

from enum import Enum
from typing import Annotated, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from scraperapi_mcp_server.execution import run_sde
from scraperapi_mcp_server.sdes.base import SDE_TOOL_ANNOTATIONS, BaseSdeParams


class GoogleTimePeriod(str, Enum):
    """Relative time window to restrict Google results to."""

    LAST_HOUR = "1H"
    LAST_DAY = "1D"
    LAST_WEEK = "1W"
    LAST_MONTH = "1M"
    LAST_YEAR = "1Y"


class _GoogleQueryParams(BaseSdeParams):
    """Base for every Google endpoint: a search query plus the shared SDE params."""

    query: Annotated[
        str,
        Field(
            description="The search query, exactly as a user would type it into Google (e.g. 'best noise cancelling headphones'). Required.",
        ),
    ]


class _GoogleSerpParams(_GoogleQueryParams):
    """Shared SERP pagination/localization params for search, news, jobs, shopping."""

    uule: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Google 'uule' geolocation string encoding a precise location to search from. Advanced use; prefer country_code for simple geo-targeting.",
        ),
    ]
    num: Annotated[
        Optional[int],
        Field(
            default=None,
            gt=0,
            description="Number of results to return on the page (e.g. 10, 20, 100). If omitted, Google's default count is used.",
        ),
    ]
    hl: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Interface/host language code for results (e.g. 'en', 'es', 'de'). Controls the language of the Google UI and localized strings.",
        ),
    ]
    gl: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Two-letter country code for the Google country edition to search (e.g. 'us', 'gb'). Influences ranking and localization.",
        ),
    ]
    start: Annotated[
        Optional[int],
        Field(
            default=None,
            ge=0,
            description="Zero-based result offset for pagination (e.g. 0 for the first page, 10 for the second when num=10).",
        ),
    ]


class GoogleSearchParams(_GoogleSerpParams):
    date_range_start: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Start of a custom date range for results, formatted MM/DD/YYYY (e.g. '01/31/2026'). Use together with date_range_end.",
        ),
    ]
    date_range_end: Annotated[
        Optional[str],
        Field(
            default=None,
            description="End of a custom date range for results, formatted MM/DD/YYYY (e.g. '02/28/2026'). Use together with date_range_start.",
        ),
    ]
    time_period: Annotated[
        Optional[GoogleTimePeriod],
        Field(
            default=None,
            description="Restrict results to a relative recent window: '1H' (hour), '1D' (day), '1W' (week), '1M' (month), or '1Y' (year).",
        ),
    ]
    include_html: Annotated[
        Optional[bool],
        Field(
            default=None,
            description="When true, include the raw HTML of the results page alongside the parsed data. Increases response size. Default: false.",
        ),
    ]
    tbs: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Raw Google 'tbs' parameter for advanced result filtering (e.g. sorting, verbatim). Advanced use.",
        ),
    ]


class GoogleNewsParams(_GoogleSerpParams):
    date_range_start: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Start of a custom date range for news results, formatted MM/DD/YYYY. Use together with date_range_end.",
        ),
    ]
    date_range_end: Annotated[
        Optional[str],
        Field(
            default=None,
            description="End of a custom date range for news results, formatted MM/DD/YYYY. Use together with date_range_start.",
        ),
    ]
    time_period: Annotated[
        Optional[GoogleTimePeriod],
        Field(
            default=None,
            description="Restrict news to a relative recent window: '1H', '1D', '1W', '1M', or '1Y'.",
        ),
    ]


class GoogleJobsParams(_GoogleSerpParams):
    pass


class GoogleShoppingParams(_GoogleSerpParams):
    include_html: Annotated[
        Optional[bool],
        Field(
            default=None,
            description="When true, include the raw HTML of the shopping results page alongside the parsed data. Increases response size. Default: false.",
        ),
    ]


class GoogleMapsSearchParams(_GoogleQueryParams):
    latitude: Annotated[
        float,
        Field(
            description="Latitude of the map center to search around, in decimal degrees (e.g. 40.7128). Required by the Google Maps endpoint.",
        ),
    ]
    longitude: Annotated[
        float,
        Field(
            description="Longitude of the map center to search around, in decimal degrees (e.g. -74.0060). Required by the Google Maps endpoint.",
        ),
    ]
    zoom: Annotated[
        Optional[int],
        Field(
            default=None,
            ge=0,
            description="Map zoom level (roughly 3=country, 10=city, 15=street). Controls the geographic radius of the search.",
        ),
    ]
    include_html: Annotated[
        Optional[bool],
        Field(
            default=None,
            description="When true, include the raw HTML of the maps results alongside the parsed data. Increases response size. Default: false.",
        ),
    ]


def register_google_tools(mcp: FastMCP) -> None:
    """Register all Google structured-data tools on the given MCP server."""

    @mcp.tool(name="google_search", annotations=SDE_TOOL_ANNOTATIONS)
    async def google_search(params: GoogleSearchParams) -> str:
        """Retrieve parsed Google Search (SERP) results for a query.

        Returns the organic results, ads, related searches, knowledge panels, and
        pagination for a Google web search — already parsed into structured JSON —
        without you having to scrape and parse the SERP HTML yourself.

        When to use:
        - Programmatic SERP data: rankings, titles, links, snippets for a keyword
        - SEO/rank tracking, competitive research, or answer-engine grounding
        - Time- or date-bounded searches (recent news-like results, date ranges)

        When NOT to use:
        - Fetching the content of a specific known URL (use the 'scrape' tool)
        - Google News, Jobs, Shopping, or Maps — use the dedicated tool for each

        Args:
            params (GoogleSearchParams): query (required) plus optional
                localization (country_code, gl, hl, uule), pagination (num, start),
                date filters (date_range_start/end, time_period), tld, output_format,
                include_html, and tbs.

        Returns:
            str: JSON (default) or CSV containing the structured search results.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_sde("/structured/google/search", params)

    @mcp.tool(name="google_news", annotations=SDE_TOOL_ANNOTATIONS)
    async def google_news(params: GoogleNewsParams) -> str:
        """Retrieve parsed Google News results for a query.

        Returns structured news articles (title, source, link, timestamp, snippet)
        for a query from Google News.

        When to use:
        - Monitoring news coverage or headlines for a topic, brand, or entity
        - Time-bounded news scans (last hour/day/week or a custom date range)

        When NOT to use:
        - General web results (use 'google_search')
        - Reading the full text of a specific article (use 'scrape' on its URL)

        Args:
            params (GoogleNewsParams): query (required) plus optional localization,
                pagination, date filters (date_range_start/end, time_period), tld,
                and output_format.

        Returns:
            str: JSON (default) or CSV containing the structured news results.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_sde("/structured/google/news", params)

    @mcp.tool(name="google_jobs", annotations=SDE_TOOL_ANNOTATIONS)
    async def google_jobs(params: GoogleJobsParams) -> str:
        """Retrieve parsed Google Jobs listings for a query.

        Returns structured job postings (title, company, location, posting age,
        source) from the Google Jobs widget for a query.

        When to use:
        - Aggregating job listings for a role, company, or location
        - Labor-market or hiring research

        When NOT to use:
        - General web or news results (use 'google_search' / 'google_news')

        Args:
            params (GoogleJobsParams): query (required) plus optional localization
                (country_code, gl, hl, uule), pagination (num, start), tld, and
                output_format.

        Returns:
            str: JSON (default) or CSV containing the structured job listings.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_sde("/structured/google/jobs", params)

    @mcp.tool(name="google_shopping", annotations=SDE_TOOL_ANNOTATIONS)
    async def google_shopping(params: GoogleShoppingParams) -> str:
        """Retrieve parsed Google Shopping product results for a query.

        Returns structured shopping listings (product title, price, merchant,
        rating, link) from Google Shopping for a query.

        When to use:
        - Price comparison and product discovery across merchants
        - Market/pricing research for a product keyword

        When NOT to use:
        - A specific marketplace's own data — use the Amazon/Walmart/eBay SDE tools
        - General web results (use 'google_search')

        Args:
            params (GoogleShoppingParams): query (required) plus optional
                localization, pagination, tld, output_format, and include_html.

        Returns:
            str: JSON (default) or CSV containing the structured shopping results.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_sde("/structured/google/shopping", params)

    @mcp.tool(name="google_maps_search", annotations=SDE_TOOL_ANNOTATIONS)
    async def google_maps_search(params: GoogleMapsSearchParams) -> str:
        """Retrieve parsed Google Maps place/business results for a query.

        Returns structured local business/place results (name, address, rating,
        reviews count, category, coordinates) from Google Maps for a query,
        optionally centered on a latitude/longitude and zoom level.

        When to use:
        - Local business discovery ('coffee shops in Austin')
        - Building local listings datasets; location-based competitive research

        When NOT to use:
        - Non-local web results (use 'google_search')
        - Driving directions or routing (not provided by this endpoint)

        Args:
            params (GoogleMapsSearchParams): query, latitude, and longitude are
                required; optional zoom, country_code, tld, output_format, and
                include_html.

        Returns:
            str: JSON (default) or CSV containing the structured maps results.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_sde("/structured/google/mapssearch", params)
