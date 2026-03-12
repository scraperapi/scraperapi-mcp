from enum import Enum
from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, Field, AnyUrl, model_validator
from scraperapi_mcp_server.utils.country_codes import COUNTRY_CODES


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

    url: Annotated[AnyUrl, Field(description="URL to scrape")]
    render: Annotated[
        bool,
        Field(
            default=False,
            description="Whether to render the page using JavaScript. Set to `True` only if the page requires JavaScript rendering to display its content.",
        ),
    ]
    country_code: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Country code to scrape from (ISO 3166-1 alpha-2, e.g. 'us', 'gb', 'de')",
        ),
    ]
    premium: Annotated[
        bool,
        Field(
            default=False,
            description="Whether to use premium scraping (incompatible with ultra_premium)",
        ),
    ]
    ultra_premium: Annotated[
        bool,
        Field(
            default=False,
            description="Whether to use ultra premium scraping (incompatible with premium)",
        ),
    ]
    device_type: Annotated[
        Optional[DeviceType],
        Field(
            default=None,
            description="Device type to scrape from. Set request to use 'mobile' or 'desktop' user agents",
        ),
    ]
    output_format: Annotated[
        OutputFormat,
        Field(
            default=OutputFormat.MARKDOWN,
            description="Output format: 'text', 'markdown', 'csv' or 'json'",
        ),
    ]
    autoparse: Annotated[
        bool,
        Field(
            default=False,
            description="Enable automatic parsing of the content for select websites",
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
