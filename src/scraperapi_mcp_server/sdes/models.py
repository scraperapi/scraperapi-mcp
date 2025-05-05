from typing import Annotated
from pydantic import BaseModel, Field, AnyUrl


# Amazon
class ScrapeAmazonProductParams(BaseModel):
    """Parameters for scraping an Amazon product."""

    asin: Annotated[str, Field(description="ASIN of the Amazon product page.")]
    tld: Annotated[str, Field(description="Top-level domain to scrape.")]
    country: Annotated[str, Field(description="Country to scrape from.")]
    output_format: Annotated[str, Field(description="Output format to scrape from. We offer 'csv' and 'json' output. JSON is default if parameter is not added.")]

    
class ScrapeAmazonSearchParams(BaseModel):
    """Parameters for scraping an Amazon search."""

    query: Annotated[str, Field(description="Query to scrape.")]
    tld: Annotated[str, Field(description="Top-level domain to scrape.")]
    country: Annotated[str, Field(description="Country to scrape from.")]
    output_format: Annotated[str, Field(description="Output format to scrape from. We offer 'csv' and 'json' output. JSON is default if parameter is not added.")]


class ScrapeAmazonOffersParams(BaseModel):
    """Parameters for scraping an Amazon offers."""
    asin: Annotated[str, Field(description="ASIN of the Amazon product page.")]
    tld: Annotated[str, Field(description="Top-level domain to scrape.")]
    country: Annotated[str, Field(description="Country to scrape from.")]
    output_format: Annotated[str, Field(description="Output format to scrape from. We offer 'csv' and 'json' output. JSON is default if parameter is not added.")]
    f_new: Annotated[bool, Field(description="Whether to scrape new offers.")]
    f_used_good: Annotated[bool, Field(description="Whether to scrape used good offers.")]
    f_used_like_new: Annotated[bool, Field(description="Whether to scrape used like new offers.")]
    f_used_very_good: Annotated[bool, Field(description="Whether to scrape used very good offers.")]
    f_used_acceptable: Annotated[bool, Field(description="Whether to scrape used acceptable offers.")]
