import pytest
from pydantic import ValidationError

from scraperapi_mcp_server.crawler import (
    CrawlerJobStartParams,
    CrawlInterval,
    CrawlSchedule,
)

VALID_REGEX = r'(?<full_url>https://example\.com/[^"]+)'


class TestValidation:
    def test_requires_depth_or_budget(self):
        with pytest.raises(ValidationError):
            CrawlerJobStartParams(
                start_url="https://example.com", url_regexp_include=VALID_REGEX
            )

    def test_max_depth_accepted(self):
        p = CrawlerJobStartParams(
            start_url="https://example.com",
            url_regexp_include=VALID_REGEX,
            max_depth=2,
        )
        assert p.max_depth == 2

    def test_requires_named_group_in_regex(self):
        with pytest.raises(ValidationError):
            CrawlerJobStartParams(
                start_url="https://example.com",
                url_regexp_include=r"https://example\.com/.*",
                max_depth=1,
            )

    def test_relative_url_named_group_ok(self):
        p = CrawlerJobStartParams(
            start_url="https://example.com",
            url_regexp_include=r'(?<relative_url>/[^"]+)',
            crawl_budget=100,
        )
        assert p.crawl_budget == 100

    def test_max_depth_must_be_positive(self):
        with pytest.raises(ValidationError):
            CrawlerJobStartParams(
                start_url="https://example.com",
                url_regexp_include=VALID_REGEX,
                max_depth=0,
            )


class TestToBody:
    def test_minimal_body(self):
        p = CrawlerJobStartParams(
            start_url="https://example.com",
            url_regexp_include=VALID_REGEX,
            crawl_budget=50,
        )
        assert p.to_body() == {
            "start_url": "https://example.com",
            "url_regexp_include": VALID_REGEX,
            "crawl_budget": 50,
        }

    def test_callback_url_wrapped_as_webhook(self):
        p = CrawlerJobStartParams(
            start_url="https://example.com",
            url_regexp_include=VALID_REGEX,
            max_depth=1,
            callback_url="https://cb.example.com/hook",
        )
        assert p.to_body()["callback"] == {
            "type": "webhook",
            "url": "https://cb.example.com/hook",
        }

    def test_schedule_interval_serialized_to_value(self):
        p = CrawlerJobStartParams(
            start_url="https://example.com",
            url_regexp_include=VALID_REGEX,
            max_depth=1,
            schedule=CrawlSchedule(interval=CrawlInterval.DAILY, name="nightly"),
        )
        schedule = p.to_body()["schedule"]
        assert schedule["interval"] == "daily"
        assert schedule["name"] == "nightly"


class TestCrawlerToolDispatch:
    @staticmethod
    async def _start(mocker):
        mock_resp = mocker.Mock()
        mock_resp.text = '{"status": "initiated", "jobId": "abc"}'
        mock_post = mocker.patch(
            "scraperapi_mcp_server.crawler.http.post",
            new_callable=mocker.AsyncMock,
            return_value=mock_resp,
        )
        from scraperapi_mcp_server.server import mcp

        await mcp.call_tool(
            "crawler_job_start",
            {
                "params": {
                    "start_url": "https://example.com",
                    "url_regexp_include": VALID_REGEX,
                    "max_depth": 1,
                }
            },
        )
        return mock_post

    @pytest.mark.asyncio
    async def test_start_posts_job_with_auth(self, mocker):
        mock_post = await self._start(mocker)

        mock_post.assert_awaited_once()
        url = mock_post.call_args.args[0]
        body = mock_post.call_args.kwargs["json"]
        assert url.endswith("/job")
        assert body["api_key"] == "test_api_key"
        assert body["start_url"] == "https://example.com"

    @pytest.mark.asyncio
    async def test_status_gets_status_endpoint(self, mocker):
        mock_resp = mocker.Mock()
        mock_resp.text = '{"done": 0}'
        mock_get = mocker.patch(
            "scraperapi_mcp_server.crawler.http.get",
            new_callable=mocker.AsyncMock,
            return_value=mock_resp,
        )
        from scraperapi_mcp_server.server import mcp

        await mcp.call_tool("crawler_job_status", {"params": {"job_id": "abc"}})

        mock_get.assert_awaited_once()
        assert mock_get.call_args.args[0].endswith("/job/abc/status")

    @pytest.mark.asyncio
    async def test_delete_calls_delete_endpoint(self, mocker):
        mock_resp = mocker.Mock()
        mock_resp.text = '{"status": "OK"}'
        mock_delete = mocker.patch(
            "scraperapi_mcp_server.crawler.http.delete",
            new_callable=mocker.AsyncMock,
            return_value=mock_resp,
        )
        from scraperapi_mcp_server.server import mcp

        await mcp.call_tool("crawler_job_delete", {"params": {"job_id": "abc"}})

        mock_delete.assert_awaited_once()
        assert mock_delete.call_args.args[0].endswith("/job/abc")
