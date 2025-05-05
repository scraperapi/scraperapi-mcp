from .base import ScraperEndpoint

amazon_product = ScraperEndpoint(
    endpoint_path="/structured/amazon/product",
    context_template="fetching Amazon product '{asin}'"
)

amazon_search = ScraperEndpoint(
    endpoint_path="/structured/amazon/search",
    context_template="fetching Amazon search results for '{query}'"
)

amazon_offers = ScraperEndpoint(
    endpoint_path="/structured/amazon/offers",
    context_template="fetching Amazon offers for '{asin}'"
)

def scrape_amazon_product(asin: str, tld: str, country: str, output_format: str) -> str:
    return amazon_product.call(asin=asin, tld=tld, country=country, output_format=output_format)

def scrape_amazon_search(query: str, tld: str, country: str, output_format: str, page: int) -> str:
    return amazon_search.call(query=query, tld=tld, country=country, output_format=output_format, page=page)

def scrape_amazon_offers(asin: str, tld: str, country: str, output_format: str, f_new: bool, f_used_good: bool, f_used_like_new: bool, f_used_very_good: bool, f_used_acceptable: bool) -> str:
    return amazon_offers.call(
        asin=asin,
        tld=tld,
        country=country,
        output_format=output_format,
        f_new=f_new,
        f_used_good=f_used_good,
        f_used_like_new=f_used_like_new,
        f_used_very_good=f_used_very_good,
        f_used_acceptable=f_used_acceptable
    )
