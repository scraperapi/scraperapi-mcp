"""Pydantic models for the ScraperAPI Crawler tools."""

from enum import Enum
from typing import Annotated, Any, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


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
