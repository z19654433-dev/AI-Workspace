"""热榜工具：获取各平台今日热门内容"""

from tools import registry
from utils.logger import get_logger
import httpx

logger = get_logger(__name__)

_TIMEOUT = 10.0
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def _fetch_json(url: str) -> dict | None:
    """通用 GET 请求 + JSON 解析"""
    headers = {"User-Agent": _USER_AGENT}
    try:
        with httpx.Client(timeout=_TIMEOUT, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()
    except httpx.TimeoutException:
        logger.warning("请求超时 %s", url)
    except httpx.HTTPStatusError as e:
        logger.warning("请求返回 %s: %s", e.response.status_code, url)
    except Exception as e:
        logger.error("请求失败 %s: %s", url, e)
    return None


def _get_github_trending() -> list[dict]:
    """GitHub 趋势项目"""
    from datetime import datetime, timedelta
    since = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    url = (f"https://api.github.com/search/repositories"
           f"?q=created:>{since}&sort=stars&order=desc&per_page=15")
    data = _fetch_json(url)
    if not data:
        return []
    return [
        {"title": repo["full_name"],
         "url": repo["html_url"],
         "desc": (repo.get("description") or "")[:80],
         "hot": f"\u2b50 {repo['stargazers_count']} stars"}
        for repo in data.get("items", [])
    ]


def _get_weibo_hot() -> list[dict]:
    """微博热搜（官方接口，无需登录）"""
    url = "https://weibo.com/ajax/side/hotSearch"
    data = _fetch_json(url)
    if not data:
        return []
    realtime = data.get("data", {}).get("realtime", [])
    return [
        {"title": item.get("word", ""),
         "url": f"https://s.weibo.com/weibo?q={item.get('word', '')}",
         "desc": "",
         "hot": f"\u706b {item.get('hot_num', '')}"}
        for item in realtime[:25]
    ]


def _get_baidu_hot() -> list[dict]:
    """百度热搜（官方接口）"""
    url = "https://top.baidu.com/api/board?tab=realtime"
    data = _fetch_json(url)
    if not data:
        return []
    results = data.get("data", {}).get("cards", [])
    items = []
    for card in results:
        for item in card.get("content", []):
            items.append({
                "title": item.get("word", item.get("query", "")),
                "url": item.get("url", "") or item.get("link", ""),
                "desc": item.get("desc", "")[:60],
                "hot": f"\u706b {item.get('hotScore', '')}",
            })
    return items[:25]


_PLATFORM_HANDLERS = {
    "github": ("GitHub", _get_github_trending),
    "weibo": ("微博", _get_weibo_hot),
    "baidu": ("百度", _get_baidu_hot),
}


def _format_output(platform_name: str, items: list[dict]) -> str:
    if not items:
        return f"{platform_name} 热榜暂时获取不到数据，请稍后重试"

    lines = [f"\U0001f525 {platform_name}热榜 TOP {len(items)}\n"]
    for i, item in enumerate(items, 1):
        title = item["title"]
        hot = item.get("hot", "")
        hot_str = f" [{hot}]" if hot else ""
        lines.append(f"{i:2d}. {title}{hot_str}")
        desc = item.get("desc", "")
        if desc:
            lines.append(f"    \u21b3 {desc}")
    return "\n".join(lines)


@registry.register(
    description="获取各平台今日热榜/热搜，免费无需API Key。支持github(GitHub趋势项目)、weibo(微博热搜)、baidu(百度热搜)"
)
def get_hotlist(platform: str = "github") -> str:
    """获取指定平台的今日热榜内容。

    Args:
        platform: 平台名称，github | weibo | baidu。默认 github。
    """
    platform = platform.lower().strip()

    if platform not in _PLATFORM_HANDLERS:
        supported = ", ".join(_PLATFORM_HANDLERS.keys())
        return f"不支持的平台: {platform}，当前支持: {supported}"

    platform_name, handler = _PLATFORM_HANDLERS[platform]
    try:
        items = handler()
    except Exception as e:
        logger.error("获取 %s 热榜失败: %s", platform, e)
        return f"获取 {platform_name} 热榜失败: {e}"

    return _format_output(platform_name, items)
