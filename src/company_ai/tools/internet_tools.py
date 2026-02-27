from __future__ import annotations

import json
import os
import re
from html import unescape
from typing import Any
from urllib.parse import parse_qs, quote_plus, urlparse
from urllib.request import Request, urlopen

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


DEFAULT_TIMEOUT_SECONDS = 15
DEFAULT_MAX_RESULTS = 5
DEFAULT_MAX_CHARS = 12000
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def _request_headers(include_json: bool = False) -> dict[str, str]:
    headers = {"User-Agent": os.getenv("INTERNET_TOOL_USER_AGENT", DEFAULT_USER_AGENT)}
    if include_json:
        headers["Content-Type"] = "application/json"
    return headers


def _timeout_seconds() -> int:
    raw_timeout = os.getenv("INTERNET_TOOL_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))
    try:
        timeout = int(raw_timeout)
    except ValueError:
        timeout = DEFAULT_TIMEOUT_SECONDS
    return max(3, min(timeout, 60))


def _extract_ddg_redirect(raw_url: str) -> str:
    parsed = urlparse(raw_url)
    query = parse_qs(parsed.query)
    if "uddg" in query and query["uddg"]:
        return query["uddg"][0]
    return raw_url


def _strip_html(html: str) -> str:
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


class InternetSearchInput(BaseModel):
    query: str = Field(description="Search query to run on the public web")
    max_results: int = Field(default=DEFAULT_MAX_RESULTS, description="Maximum number of results to return")


class ReadWebpageInput(BaseModel):
    url: str = Field(description="Absolute HTTP/HTTPS URL to fetch")
    max_chars: int = Field(default=DEFAULT_MAX_CHARS, description="Maximum characters to return")


class InternetSearchTool(BaseTool):
    name: str = "internet_search"
    description: str = "Search the internet for current information and return top results."
    args_schema: type[BaseModel] = InternetSearchInput

    def _run(self, query: str, max_results: int = DEFAULT_MAX_RESULTS) -> str:
        query = query.strip()
        if not query:
            return json.dumps({"error": "query cannot be empty"}, indent=2)

        max_results = max(1, min(max_results, 10))
        serper_api_key = os.getenv("SERPER_API_KEY", "").strip()
        try:
            if serper_api_key:
                return self._search_serper(query=query, max_results=max_results, api_key=serper_api_key)
            return self._search_duckduckgo(query=query, max_results=max_results)
        except Exception as exc:  # noqa: BLE001
            return json.dumps({"error": f"internet_search failed: {exc}", "query": query}, indent=2)

    def _search_serper(self, query: str, max_results: int, api_key: str) -> str:
        request_body = json.dumps({"q": query, "num": max_results}).encode("utf-8")
        request = Request(
            url="https://google.serper.dev/search",
            data=request_body,
            headers={**_request_headers(include_json=True), "X-API-KEY": api_key},
            method="POST",
        )
        with urlopen(request, timeout=_timeout_seconds()) as response:
            payload = json.loads(response.read().decode("utf-8", errors="replace"))

        organic_results = payload.get("organic", [])[:max_results]
        results = [
            {
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
            }
            for item in organic_results
        ]
        return json.dumps({"provider": "serper", "query": query, "results": results}, indent=2)

    def _search_duckduckgo(self, query: str, max_results: int) -> str:
        query_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
        request = Request(url=query_url, headers=_request_headers())
        with urlopen(request, timeout=_timeout_seconds()) as response:
            html = response.read().decode("utf-8", errors="replace")

        link_pattern = re.compile(
            r'(?s)<a[^>]*class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
        )
        snippet_pattern = re.compile(r'(?s)<a[^>]*class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</a>')
        link_matches = link_pattern.findall(html)
        snippet_matches = [_strip_html(match) for match in snippet_pattern.findall(html)]

        results: list[dict[str, Any]] = []
        for index, (raw_url, raw_title) in enumerate(link_matches[:max_results]):
            results.append(
                {
                    "title": _strip_html(raw_title),
                    "url": _extract_ddg_redirect(unescape(raw_url)),
                    "snippet": snippet_matches[index] if index < len(snippet_matches) else "",
                }
            )
        return json.dumps({"provider": "duckduckgo", "query": query, "results": results}, indent=2)


class ReadWebpageTool(BaseTool):
    name: str = "read_webpage"
    description: str = "Fetch and extract readable text from a public webpage."
    args_schema: type[BaseModel] = ReadWebpageInput

    def _run(self, url: str, max_chars: int = DEFAULT_MAX_CHARS) -> str:
        url = url.strip()
        if not url.lower().startswith(("http://", "https://")):
            return json.dumps({"error": "url must start with http:// or https://"}, indent=2)

        max_chars = max(1000, min(max_chars, 30000))
        try:
            request = Request(url=url, headers=_request_headers())
            with urlopen(request, timeout=_timeout_seconds()) as response:
                body = response.read()
                content_type = response.headers.get("Content-Type", "")

            decoded = body.decode("utf-8", errors="replace")
            text_content = _strip_html(decoded) if "text/html" in content_type.lower() else decoded
            excerpt = text_content[:max_chars]

            return json.dumps(
                {
                    "url": url,
                    "content_type": content_type,
                    "content_chars": len(text_content),
                    "excerpt": excerpt,
                },
                indent=2,
            )
        except Exception as exc:  # noqa: BLE001
            return json.dumps({"error": f"read_webpage failed: {exc}", "url": url}, indent=2)


def build_internet_tools() -> list[BaseTool]:
    return [InternetSearchTool(), ReadWebpageTool()]
