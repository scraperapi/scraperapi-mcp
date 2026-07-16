"""Shared foundation for ScraperAPI Structured Data Endpoint (SDE) tools."""

from enum import Enum
from typing import Annotated, Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from scraperapi_mcp_server.config import settings
from scraperapi_mcp_server.utils import http


class SdeOutputFormat(str, Enum):
    """Output format for structured-data endpoints. Only JSON and CSV apply."""

    JSON = "json"
    CSV = "csv"


class BaseSdeParams(BaseModel):
    """Optional parameters common to (nearly) all structured-data endpoints.

    Family models subclass this and add their required input (e.g. ``asin``,
    ``query``, ``url``) plus any family-specific optional params.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        populate_by_name=True,
    )

    output_format: Annotated[
        SdeOutputFormat,
        Field(
            default=SdeOutputFormat.JSON,
            description="Response format for the structured data. 'json' (default) returns a parsed JSON object; 'csv' returns comma-separated rows. No other formats are supported by structured-data endpoints.",
        ),
    ]
    tld: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Top-level domain of the target marketplace/site to query (e.g. 'com', 'co.uk', 'de'). Use this to target a specific regional storefront. If omitted, the endpoint's default TLD is used.",
        ),
    ]
    country_code: Annotated[
        Optional[str],
        Field(
            default=None,
            description="ISO 3166-1 alpha-2 country code used to geo-target the request (e.g. 'us', 'gb', 'de'). Affects localized results such as pricing and availability.",
        ),
    ]

    def query_params(self) -> dict[str, Any]:
        """Serialize the set fields to a query dict for the ScraperAPI request.

        Unset (``None``) fields are omitted, enum values are unwrapped to their
        underlying string, and fields are emitted under their serialization
        alias when one is defined.
        """
        data = self.model_dump(by_alias=True, exclude_none=True)
        return {
            key: (value.value if isinstance(value, Enum) else value)
            for key, value in data.items()
        }


async def fetch_sde(path: str, params: BaseSdeParams) -> str:
    """Call a structured-data endpoint and return the raw response body.

    Args:
        path: The endpoint path including the ``/structured`` prefix, e.g.
            ``"/structured/amazon/product"``.
        params: A populated :class:`BaseSdeParams` subclass instance.

    Returns:
        The response body as text — a JSON string by default, or CSV when
        ``output_format='csv'``.

    Raises:
        ScraperAPIError: If the request fails (propagated from the HTTP layer).
    """
    query = params.query_params()
    query["api_key"] = settings.API_KEY
    query["scraper_sdk"] = settings.SCRAPER_SDK
    url = f"{settings.API_URL}{path}"
    response = await http.get(url, params=query)
    return response.text
