"""ScraperAPI AI Parser tools.

The AI parser (``AIPARSER_URL``) works in two phases:

1. **Create** a reusable parser from a few example URLs (``ai_parser_create``).
   Generation is asynchronous — it returns a parser id immediately and you poll
   ``ai_parser_get_details`` until its status is ``FINISHED``.
2. **Parse** any URL with that parser (``ai_parser_parse_url``) to get structured JSON.

Auth: the ``api_key`` goes in the JSON body for create/update (POST/PATCH) and
in the query string for get/parse/list/delete (GET/DELETE), matching the service.
"""

from typing import Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from scraperapi_mcp_server.aiparser.models import (
    AiParseParams,
    AiParserCreateParams,
    AiParserDeleteParams,
    AiParserGetParams,
    AiParserUpdateParams,
)
from scraperapi_mcp_server.config import settings
from scraperapi_mcp_server.execution import run_request
from scraperapi_mcp_server.utils import http

# Creating/updating a parser generates a parser and may consume credits: not
# read-only, not idempotent, but not destructive.
_CREATE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)
# Reading parser details/list, and parsing a URL, don't change parser state.
_READ_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)
_DELETE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=True,
    openWorldHint=True,
)


def _parser_path(base: str, parser_id: str, version: Optional[int]) -> str:
    """Build a '/base/id' path, appending '/version' when a version is given."""
    path = f"/{base}/{parser_id}"
    if version is not None:
        path += f"/{version}"
    return path


def register_aiparser_tools(mcp: FastMCP) -> None:
    """Register all AI parser tools on the given MCP server."""

    @mcp.tool(name="ai_parser_create", annotations=_CREATE_ANNOTATIONS)
    async def ai_parser_create(params: AiParserCreateParams) -> str:
        """Create a reusable AI parser from example URLs.

        Generates a parser that extracts structured data from pages sharing a
        layout. Generation is ASYNCHRONOUS: this returns a parser id and version
        immediately (e.g. {"id": "...", "version": 0}); poll 'ai_parser_get_details' until
        its status is 'FINISHED' before calling 'ai_parser_parse_url'.

        When to use:
        - You want repeatable structured extraction across many similar pages
          (e.g. product pages of one site) and there's no dedicated SDE for it
        - You can provide 1–10 example URLs of the same page type

        When NOT to use:
        - A one-off fetch (use 'scrape') or a supported marketplace/SERP (use the SDE)

        Args:
            params (AiParserCreateParams): name and urls (1–10) are required;
                optional scraper_params (fetch options) and fields (pre-declared
                output schema).

        Returns:
            str: JSON with the new parser's id and version.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, the
                inputs are invalid, or the request fails.
        """
        body = params.model_dump(mode="json", exclude_none=True)
        body["api_key"] = settings.API_KEY
        return await run_request(
            http.post(f"{settings.AIPARSER_URL}/parsers", json=body)
        )

    @mcp.tool(name="ai_parser_get_details", annotations=_READ_ANNOTATIONS)
    async def ai_parser_get_details(params: AiParserGetParams) -> str:
        """Get an AI parser's details and generation status.

        Returns the parser's status ('GENERATING', 'FINISHED', or 'FAILED'), its
        fields, example results, and any error. Poll this after 'ai_parser_create'
        (or after a field-editing 'ai_parser_update') until status is 'FINISHED'.

        When to use:
        - Polling a parser's status after create/update until it is 'FINISHED'
        - Inspecting a parser's fields before parsing with it

        When NOT to use:
        - Extracting data from a page (use 'ai_parser_parse_url')

        Args:
            params (AiParserGetParams): parser_id (required) and optional version.

        Returns:
            str: JSON with the parser details and status.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        path = _parser_path("parsers", params.parser_id, params.version)
        return await run_request(
            http.get(
                f"{settings.AIPARSER_URL}{path}", params={"api_key": settings.API_KEY}
            )
        )

    @mcp.tool(name="ai_parser_parse_url", annotations=_READ_ANNOTATIONS)
    async def ai_parser_parse_url(params: AiParseParams) -> str:
        """Parse a URL with an existing AI parser and return structured data.

        Scrapes the given URL and applies the parser, returning the extracted data
        as structured JSON keyed by the parser's fields. The parser must already be
        'FINISHED' (see 'ai_parser_create' / 'ai_parser_get_details'). Costs 1 credit per call.

        When to use:
        - Extracting structured data from a page using a FINISHED parser
        - Applying one parser across many similarly structured pages

        When NOT to use:
        - The parser isn't ready yet (create it, then poll 'ai_parser_get_details')
        - A one-off fetch (use 'scrape') or a supported marketplace/SERP (use the SDE)

        Args:
            params (AiParseParams): parser_id and url are required; optional version.

        Returns:
            str: JSON of the form {"parser": ..., "version": ..., "result": {...}}.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        path = _parser_path("parse", params.parser_id, params.version)
        return await run_request(
            http.get(
                f"{settings.AIPARSER_URL}{path}",
                params={"api_key": settings.API_KEY, "url": params.url},
            )
        )

    @mcp.tool(name="ai_parser_list", annotations=_READ_ANNOTATIONS)
    async def ai_parser_list() -> str:
        """List the AI parsers on your account.

        Returns each parser's id, name, status, version, and generation time.

        When to use:
        - Discovering existing parsers and their ids/status before reusing one

        When NOT to use:
        - Getting one parser's full fields/details (use 'ai_parser_get_details')

        Returns:
            str: JSON array of parser summaries.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_request(
            http.get(
                f"{settings.AIPARSER_URL}/parsers",
                params={"api_key": settings.API_KEY},
            )
        )

    @mcp.tool(name="ai_parser_delete", annotations=_DELETE_ANNOTATIONS)
    async def ai_parser_delete(params: AiParserDeleteParams) -> str:
        """Delete an AI parser.

        Permanently removes the parser (and all its versions) from your account.

        When to use:
        - Removing a parser you no longer need (e.g. to stay under plan limits)

        When NOT to use:
        - Changing a parser's fields (use 'ai_parser_update'); deletion is permanent

        Args:
            params (AiParserDeleteParams): parser_id (required).

        Returns:
            str: Empty on success (HTTP 204).

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_request(
            http.delete(
                f"{settings.AIPARSER_URL}/parsers/{params.parser_id}",
                params={"api_key": settings.API_KEY},
            )
        )

    @mcp.tool(name="ai_parser_update", annotations=_CREATE_ANNOTATIONS)
    async def ai_parser_update(params: AiParserUpdateParams) -> str:
        """Edit an AI parser's fields, creating a new version.

        Add, modify, rename, or remove fields. Adding or modifying fields triggers
        asynchronous regeneration (poll 'ai_parser_get_details' until 'FINISHED'); renaming
        or removing fields is applied immediately.

        When to use:
        - Adjusting an existing parser's fields (add/modify/rename/remove) rather
          than recreating it

        When NOT to use:
        - Creating a brand-new parser (use 'ai_parser_create')

        Args:
            params (AiParserUpdateParams): parser_id (required) and optional version,
                plus any of add_fields, modify_fields, rename_fields, remove_fields.

        Returns:
            str: JSON with the parser id and (new) version.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, the
                inputs are invalid, or the request fails.
        """
        path = _parser_path("parsers", params.parser_id, params.version)
        body = params.model_dump(
            mode="json", exclude_none=True, exclude={"parser_id", "version"}
        )
        body["api_key"] = settings.API_KEY
        return await run_request(http.patch(f"{settings.AIPARSER_URL}{path}", json=body))
