from typing import Annotated
from pydantic import BaseModel, Field, AnyUrl


class Scrape(BaseModel):
    """Parameters for scraping a URL."""

    url: Annotated[AnyUrl, Field(description="URL to scrape")]
    render: Annotated[
        bool,
        Field(
            default=False,
            description="Whether to render the page using JavaScript. Set to `True` only if the page requires JavaScript rendering to display its content.",
        ),
    ]
    country_code: Annotated[
        str, Field(default=None, description="Country code to scrape from")
    ]
    premium: Annotated[
        bool, Field(default=False, description="Whether to use premium scraping")
    ]
    ultra_premium: Annotated[
        bool, Field(default=False, description="Whether to use ultra premium scraping")
    ]
    device_type: Annotated[
        str,
        Field(
            default=None,
            description="Device type to scrape from. Set request to use `mobile` or `desktop` user agents",
        ),
    ]
