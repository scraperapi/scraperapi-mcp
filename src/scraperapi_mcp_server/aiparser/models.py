"""Pydantic models for the ScraperAPI AI Parser tools."""

from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field


class DeviceType(str, Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"


class FieldType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    ARRAY = "array"


class ParserScraperParams(BaseModel):
    """ScraperAPI options used when fetching the example/target pages."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    render: Annotated[
        Optional[bool], Field(default=None, description="Enable JavaScript rendering.")
    ]
    country_code: Annotated[
        Optional[str],
        Field(
            default=None,
            pattern=r"^[a-zA-Z]{2}$",
            description="ISO 2-letter country code for geo-targeting.",
        ),
    ]
    premium: Annotated[
        Optional[bool], Field(default=None, description="Use premium proxies.")
    ]
    session_number: Annotated[
        Optional[int],
        Field(default=None, ge=1, description="Sticky session id to reuse an IP."),
    ]
    keep_headers: Annotated[
        Optional[bool], Field(default=None, description="Forward your custom headers.")
    ]
    device_type: Annotated[
        Optional[DeviceType],
        Field(default=None, description="Emulate 'desktop' or 'mobile'."),
    ]
    ultra_premium: Annotated[
        Optional[bool], Field(default=None, description="Use advanced anti-bot bypass.")
    ]
    follow_redirect: Annotated[
        Optional[bool], Field(default=None, description="Follow HTTP redirects.")
    ]
    retry_404: Annotated[
        Optional[bool], Field(default=None, description="Retry on HTTP 404.")
    ]


class ParserField(BaseModel):
    """A field the parser should extract."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: Annotated[
        str,
        Field(
            description="Field name. Use dot notation for nesting, e.g. 'products.price'."
        ),
    ]
    description: Annotated[
        str,
        Field(
            description="What this field is, in plain language — guides the AI extraction."
        ),
    ]
    type: Annotated[
        Optional[FieldType],
        Field(default=None, description="Expected type: 'string', 'number', or 'array'."),
    ]
    selector: Annotated[
        Optional[str],
        Field(default=None, description="Optional CSS/XPath selector hint for the field."),
    ]


class RenameField(BaseModel):
    """A field rename instruction."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: Annotated[str, Field(description="Current field name.")]
    new_name: Annotated[str, Field(description="New field name.")]


class AiParserCreateParams(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: Annotated[
        str, Field(min_length=1, description="A name for the parser. Required.")
    ]
    urls: Annotated[
        list[str],
        Field(
            min_length=1,
            max_length=3,
            description="1 to 3 example URLs of the same page type that the parser learns from (they should share the same structure). Required.",
        ),
    ]
    scraper_params: Annotated[
        Optional[ParserScraperParams],
        Field(
            default=None,
            description="Optional ScraperAPI fetch options for the example pages.",
        ),
    ]
    fields: Annotated[
        Optional[list[ParserField]],
        Field(
            default=None,
            description="Optional list of fields to extract, pre-declaring the output schema to guide generation. If omitted, the AI infers fields.",
        ),
    ]


class AiParserGetParams(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    parser_id: Annotated[
        str, Field(description="The parser id returned by ai_parser_create. Required.")
    ]
    version: Annotated[
        Optional[int],
        Field(
            default=None, ge=0, description="Specific parser version. Defaults to the latest."
        ),
    ]


class AiParseParams(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    parser_id: Annotated[str, Field(description="The parser id to run. Required.")]
    url: Annotated[
        str, Field(description="The URL to scrape and parse with the parser. Required.")
    ]
    version: Annotated[
        Optional[int],
        Field(
            default=None, ge=0, description="Specific parser version. Defaults to the latest."
        ),
    ]


class AiParserDeleteParams(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    parser_id: Annotated[str, Field(description="The parser id to delete. Required.")]


class AiParserUpdateParams(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    parser_id: Annotated[str, Field(description="The parser id to update. Required.")]
    version: Annotated[
        Optional[int],
        Field(
            default=None,
            ge=0,
            description="Specific parser version to base the update on. Defaults to the latest.",
        ),
    ]
    add_fields: Annotated[
        Optional[list[ParserField]],
        Field(default=None, description="Fields to add (triggers async regeneration)."),
    ]
    modify_fields: Annotated[
        Optional[list[ParserField]],
        Field(
            default=None,
            description="Existing fields to modify (triggers async regeneration).",
        ),
    ]
    rename_fields: Annotated[
        Optional[list[RenameField]],
        Field(default=None, description="Fields to rename (applied immediately)."),
    ]
    remove_fields: Annotated[
        Optional[list[str]],
        Field(
            default=None, description="Names of fields to remove (applied immediately)."
        ),
    ]
