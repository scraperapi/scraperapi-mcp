"""ScraperAPI Crawler tools.

The crawler is an asynchronous service on a separate host (``CRAWLER_URL``):
submit a job and receive a job id immediately, then poll for status. These tools 
POST a JSON body (with ``api_key`` in the body, not the query string).

The server does NOT poll internally. ``crawler_job_start``
returns the job id and the caller polls ``crawler_job_status`` until the job is done.
Per-page results are delivered to the optional ``callback_url`` webhook.
"""

from enum import Enum
from typing import Annotated, Any, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BaseModel, ConfigDict, Field, model_validator

from scraperapi_mcp_server.config import settings
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


class CrawlInterval(str, Enum):
    """Recurrence interval for a scheduled (recurring) crawl."""

    ONCE = "once"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class CrawlSchedule(BaseModel):
    """Schedule configuration to turn a crawl into a recurring project."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    interval: Annotated[
        Optional[CrawlInterval],
        Field(
            default=None,
            description="Recurrence interval: 'once', 'hourly', 'daily', 'weekly', or 'monthly'.",
        ),
    ]
    cron: Annotated[
        Optional[str],
        Field(
            default=None,
            description="A cron expression for custom scheduling, as an alternative to interval.",
        ),
    ]
    name: Annotated[
        Optional[str],
        Field(
            default=None, description="A human-readable name for the scheduled project."
        ),
    ]


class CrawlerJobStartParams(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    start_url: Annotated[
        str,
        Field(
            description="The URL where crawling begins (depth 0). Required.",
        ),
    ]
    url_regexp_include: Annotated[
        str,
        Field(
            description="Regular expression used to find URLs to crawl on each page. Must include a named group '(?<full_url>...)' for absolute URLs and/or '(?<relative_url>...)' for relative URLs. Required.",
        ),
    ]
    max_depth: Annotated[
        Optional[int],
        Field(
            default=None,
            gt=0,
            description="Maximum crawl depth (the start URL is depth 0). Provide either max_depth or crawl_budget.",
        ),
    ]
    crawl_budget: Annotated[
        Optional[int],
        Field(
            default=None,
            gt=0,
            description="Maximum ScraperAPI credits the crawl may consume. Provide either max_depth or crawl_budget.",
        ),
    ]
    url_regexp_exclude: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Regular expression for URLs to exclude from crawling.",
        ),
    ]
    api_params: Annotated[
        Optional[dict[str, Any]],
        Field(
            default=None,
            description="Per-scrape controls applied to each page, e.g. {'render': true, 'country_code': 'us', 'premium': true, 'device_type': 'desktop', 'output_format': 'markdown'}.",
        ),
    ]
    callback_url: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Webhook URL to receive per-page results and the final job summary as the crawl progresses.",
        ),
    ]
    additional_data: Annotated[
        Optional[dict[str, Any]],
        Field(
            default=None,
            description="Arbitrary metadata to attach to the job (echoed back in results).",
        ),
    ]
    schedule: Annotated[
        Optional[CrawlSchedule],
        Field(
            default=None,
            description="Optional schedule to run the crawl as a recurring project instead of a one-off.",
        ),
    ]
    enabled: Annotated[
        Optional[bool],
        Field(
            default=None,
            description="For scheduled projects, whether the schedule is enabled. Defaults to true.",
        ),
    ]

    @model_validator(mode="after")
    def validate_params(self):
        if self.max_depth is None and self.crawl_budget is None:
            raise ValueError(
                "Provide either max_depth or crawl_budget to bound the crawl."
            )
        if (
            "(?<full_url>" not in self.url_regexp_include
            and "(?<relative_url>" not in self.url_regexp_include
        ):
            raise ValueError(
                "url_regexp_include must contain a named group '(?<full_url>...)' "
                "and/or '(?<relative_url>...)'."
            )
        return self

    def to_body(self) -> dict[str, Any]:
        """Assemble the snake_case JSON body for POST /job (excluding auth)."""
        body: dict[str, Any] = {
            "start_url": self.start_url,
            "url_regexp_include": self.url_regexp_include,
        }
        if self.max_depth is not None:
            body["max_depth"] = self.max_depth
        if self.crawl_budget is not None:
            body["crawl_budget"] = self.crawl_budget
        if self.url_regexp_exclude:
            body["url_regexp_exclude"] = self.url_regexp_exclude
        if self.api_params:
            body["api_params"] = self.api_params
        if self.callback_url:
            body["callback"] = {"type": "webhook", "url": self.callback_url}
        if self.additional_data:
            body["additional_data"] = self.additional_data
        if self.schedule is not None:
            schedule = self.schedule.model_dump(exclude_none=True)
            interval = schedule.get("interval")
            if isinstance(interval, CrawlInterval):
                schedule["interval"] = interval.value
            body["schedule"] = schedule
        if self.enabled is not None:
            body["enabled"] = self.enabled
        return body


class CrawlerJobRefParams(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    job_id: Annotated[
        str,
        Field(
            description="The crawler job id returned by crawler_job_start. Required."
        ),
    ]


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
