from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, Field, AnyUrl, model_validator
from scraperapi_mcp_server.utils.country_codes import COUNTRY_CODES


class ScrapeError(Exception):
    """Raised when a scrape operation fails. Carries an actionable error message."""

    pass


@dataclass
class ScrapeResult:
    """Result of a scrape operation, supporting both text and image content."""

    text: Optional[str] = None
    image_data: Optional[bytes] = None
    mime_type: Optional[str] = None

    @property
    def is_image(self) -> bool:
        return self.image_data is not None


class OutputFormat(str, Enum):
    TEXT = "text"
    MARKDOWN = "markdown"
    CSV = "csv"
    JSON = "json"


class DeviceType(str, Enum):
    MOBILE = "mobile"
    DESKTOP = "desktop"


class Scrape(BaseModel):
    """Parameters for scraping a URL."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    url: Annotated[
        AnyUrl,
        Field(
            description="The full URL of the web page or image to scrape (e.g. 'https://example.com/page'). Must be a valid HTTP or HTTPS URL.",
        ),
    ]
    render: Annotated[
        bool,
        Field(
            default=False,
            description="Enable headless browser rendering for pages that load content dynamically via JavaScript. Default: false. Set to true only when the target page uses client-side rendering (e.g. SPAs, React/Angular apps) and the needed content is not in the initial HTML. Most pages do not require this. Enabling it increases response time and cost.",
        ),
    ]
    country_code: Annotated[
        Optional[str],
        Field(
            default=None,
            description="ISO 3166-1 alpha-2 country code to route the request through a proxy in that country (e.g. 'us', 'gb', 'de', 'jp'). Use this when the target website serves different content based on geographic location.",
        ),
    ]
    premium: Annotated[
        bool,
        Field(
            default=False,
            description="Use premium residential and mobile proxies for higher success rates on difficult-to-scrape websites. Default: false. Increases cost per request. Cannot be combined with ultra_premium.",
        ),
    ]
    ultra_premium: Annotated[
        bool,
        Field(
            default=False,
            description="Use ultra-premium proxies and advanced anti-bot bypass mechanisms for the most protected websites. Default: false. Highest cost per request. Cannot be combined with premium.",
        ),
    ]
    device_type: Annotated[
        Optional[DeviceType],
        Field(
            default=None,
            description="Emulate a specific device type by setting the User-Agent header. Use 'desktop' or 'mobile' when the target site serves different content or layouts based on the device. If omitted, the default User-Agent is used.",
        ),
    ]
    output_format: Annotated[
        OutputFormat,
        Field(
            default=OutputFormat.MARKDOWN,
            description="Format for the scraped text output. 'markdown' (default): clean readable markdown. 'text': plain text without formatting. 'csv': comma-separated values (requires autoparse=true for structured sites). 'json': JSON object (requires autoparse=true for structured sites).",
        ),
    ]
    autoparse: Annotated[
        bool,
        Field(
            default=False,
            description="Enable ScraperAPI's automatic structured data extraction for supported websites (e.g. Amazon, Google, Walmart). Default: false. When enabled, returns pre-parsed structured data. Should be set to true when using output_format 'csv' or 'json'. Has no effect on unsupported websites.",
        ),
    ]

    @model_validator(mode="after")
    def validate_params(self):
        if self.premium and self.ultra_premium:
            raise ValueError(
                "premium and ultra_premium cannot both be enabled. Choose one or the other."
            )
        if self.country_code is not None:
            code = self.country_code.strip().lower()
            self.__dict__["country_code"] = COUNTRY_CODES.get(code, code)
        return self
