class ScraperAPIError(Exception):
    """Raised when a ScraperAPI request fails.

    Carries an actionable, human-readable message that tool handlers surface to
    the MCP client as a ToolError so the model can self-correct.
    """

    pass
