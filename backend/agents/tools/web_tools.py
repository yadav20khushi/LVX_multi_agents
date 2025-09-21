from typing import List, Dict, Any
import httpx
import re
import urllib.parse as urlparse

USER_AGENT = "LVX/0.1 (+research; verification)"
DDG_HTML = "https://html.duckduckgo.com/html"

def _clean_snippet(text: str, max_len: int = 300) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text[:max_len]

def _decode_ddg_link(url: str) -> str:
    # DDG wraps links like /l/?kh=-1&uddg=<urlencoded_target>
    try:
        parsed = urlparse.urlparse(url)
        if parsed.netloc.endswith("duckduckgo.com") and parsed.path.startswith("/l/"):
            qs = urlparse.parse_qs(parsed.query)
            if "uddg" in qs and qs["uddg"]:
                return urlparse.unquote(qs["uddg"][0])
    except Exception:
        pass
    return url

def web_search_tool(
    query: str,
    top_k: int = 5,
    fetch_snippets: bool = False,
    max_results: int = 5
) -> Dict[str, Any]:
    """
    Lightweight web search via DuckDuckGo HTML endpoint for quick verification.
    Returns a list of {title, url, snippet?}. Avoids redirects by decoding DDG link wrappers.
    Caps total results to avoid excessive calls.
    """
    if not query or not query.strip():
        return {"status": "error", "error": "empty query"}
    try:
        params = {"q": query.strip(), "kl": "us-en"}
        headers = {"User-Agent": USER_AGENT}
        r = httpx.get(DDG_HTML, params=params, headers=headers, timeout=15, follow_redirects=True)
        r.raise_for_status()

        links = []
        for m in re.finditer(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r.text, re.S | re.I):
            raw = m.group(1)
            title = re.sub("<.*?>", "", m.group(2))
            url = _decode_ddg_link(raw)
            if not url.startswith(("http://", "https://")):
                continue
            links.append({"title": _clean_snippet(title, 120), "url": url})
            if len(links) >= min(top_k, max_results):
                break

        results: List[Dict[str, Any]] = []
        if fetch_snippets:
            # Hard cap snippet fetches as well
            to_fetch = links[:min(len(links), max_results)]
            for link in to_fetch:
                snippet = ""
                try:
                    hr = httpx.get(link["url"], headers=headers, timeout=10, follow_redirects=True)
                    text = hr.text
                    snippet_match = re.search(r"<p[^>]*>(.*?)</p>", text, re.S | re.I)
                    snippet = _clean_snippet(re.sub("<.*?>", "", snippet_match.group(1)) if snippet_match else "")
                except Exception:
                    snippet = ""
                results.append({"title": link["title"], "url": link["url"], "snippet": snippet})
        else:
            for link in links:
                results.append({"title": link["title"], "url": link["url"]})

        return {"status": "success", "results": results}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def web_fetch_tool(url: str, max_chars: int = 8000, timeout_s: int = 20) -> Dict[str, Any]:
    """
    Fetch a single URL and return a cleaned text excerpt to cite in A2's memo.
    """
    if not url or not url.startswith(("http://", "https://")):
        return {"status": "error", "error": "invalid url"}
    try:
        headers = {"User-Agent": USER_AGENT}
        r = httpx.get(url, headers=headers, timeout=timeout_s, follow_redirects=True)
        r.raise_for_status()
        # Strip tags very roughly for prototype
        text = re.sub("<script.*?</script>|<style.*?</style>", " ", r.text, flags=re.S | re.I)
        text = re.sub("<.*?>", " ", text, flags=re.S)
        text = re.sub(r"\s+", " ", text).strip()
        return {"status": "success", "url": url, "content": text[:max_chars]}
    except Exception as e:
        return {"status": "error", "error": str(e), "url": url}
