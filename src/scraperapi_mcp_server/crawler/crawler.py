"""ScraperAPI Crawler tools.

The crawler is an asynchronous service on a separate host (``CRAWLER_URL``):
submit a job and receive a job id immediately, then poll for status. These tools
POST a JSON body (with ``api_key`` in the body, not the query string).

The server does NOT poll internally. ``crawler_job_start`` returns the job id and
the caller polls ``crawler_job_status`` until the job is done. Per-page results
are delivered to the optional ``callback_url`` webhook.
"""

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from scraperapi_mcp_server.config import settings
from scraperapi_mcp_server.crawler.models import (
    CrawlerJobRefParams,
    CrawlerJobStartParams,
)
from scraperapi_mcp_server.execution import run_request
from scraperapi_mcp_server.utils import http

# Starting a crawl is a non-read-only, non-idempotent action (each call creates a
# new job and consumes credits), but it is not destructive.
_START_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)
_STATUS_ANNOTATIONS = ToolAnnotations(
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


def register_crawler_tools(mcp: FastMCP) -> None:
    """Register all crawler tools on the given MCP server."""

    @mcp.tool(name="crawler_job_start", annotations=_START_ANNOTATIONS)
    async def crawler_job_start(params: CrawlerJobStartParams) -> str:
        """Start a ScraperAPI crawl job from a starting URL.

        Submits an asynchronous crawl that follows links matching a regex outward
        from start_url and scrapes each page. Returns immediately with a job id and
        status (e.g. {"status": "initiated", "jobId": "..."}); the crawl runs in the
        background. Poll 'crawler_job_status' with the returned job id to track
        progress, and/or provide a callback_url webhook to receive results.

        When to use:
        - Crawling multiple linked pages of a site (not a single known URL)
        - Building a dataset by following links to a depth or credit budget

        When NOT to use:
        - Fetching one known URL (use the 'scrape' tool)
        - A structured marketplace/SERP lookup (use the relevant SDE tool)

        Args:
            params (CrawlerJobStartParams): start_url and url_regexp_include are
                required; provide either max_depth or crawl_budget to bound the
                crawl. Optional: url_regexp_exclude, api_params, callback_url,
                additional_data, schedule, enabled.

        Returns:
            str: JSON with the job id and initial status.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, the
                inputs are invalid, or the request fails.
        """
        body = params.to_body()
        body["api_key"] = settings.API_KEY
        return await run_request(http.post(f"{settings.CRAWLER_URL}/job", json=body))

    @mcp.tool(name="crawler_job_status", annotations=_STATUS_ANNOTATIONS)
    async def crawler_job_status(params: CrawlerJobRefParams) -> str:
        """Get the status of a ScraperAPI crawl job.

        Returns counts of pages that are done, failed, and active for the job,
        letting you track progress and detect completion. Poll this after
        'crawler_job_start' until the job is finished.

        When to use:
        - Tracking progress or detecting completion of a job from 'crawler_job_start'

        When NOT to use:
        - Retrieving the crawled page contents (those are delivered to the job's
          callback_url webhook, not returned here)

        Args:
            params (CrawlerJobRefParams): job_id (required) — the id returned by
                crawler_job_start.

        Returns:
            str: JSON with the job's page counts (done/failed/active).

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_request(
            http.get(f"{settings.CRAWLER_URL}/job/{params.job_id}/status")
        )

    @mcp.tool(name="crawler_job_delete", annotations=_DELETE_ANNOTATIONS)
    async def crawler_job_delete(params: CrawlerJobRefParams) -> str:
        """Cancel and delete a ScraperAPI crawl job.

        Irreversibly cancels a running crawl job and removes it. Use this to stop a
        crawl you no longer need.

        When to use:
        - Stopping a running crawl you started and no longer want

        When NOT to use:
        - Pausing temporarily — this permanently cancels the job (there is no resume)

        Args:
            params (CrawlerJobRefParams): job_id (required) — the id returned by
                crawler_job_start.

        Returns:
            str: JSON confirming the job was cancelled.

        Raises:
            ToolError: If the API key is missing, the rate limit is exceeded, or
                the request fails.
        """
        return await run_request(
            http.delete(f"{settings.CRAWLER_URL}/job/{params.job_id}")
        )
