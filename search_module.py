"""Search module using DuckDuckGo."""

from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import DuckDuckGoSearchException


def search_event(event: str, max_results: int = 5, timeout: int = 30) -> str:
    """Search for event information using DuckDuckGo and return summary text."""
    results = []
    try:
        with DDGS(timeout=timeout) as ddgs:
            search_results = list(ddgs.text(event, max_results=max_results))
        for r in search_results:
            title = r.get("title", "")
            body = r.get("body", "")
            if title or body:
                results.append(f"- {title}\n  {body}")
    except DuckDuckGoSearchException:
        return f"搜尋逾時或失敗，使用事件文字作為上下文。事件: {event}"
    return "\n".join(results) if results else f"No search results for: {event}"
