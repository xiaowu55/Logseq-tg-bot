import re
import requests
from typing import Optional
from bs4 import BeautifulSoup
import urllib.parse


def get_web_page_title(url: str) -> Optional[str]:
    """获取网页标题

    Args:
        url: 网页 URL

    Returns:
        网页标题，如果获取失败则返回 None
    """
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            if title := soup.title:
                return title.string.strip()
    except Exception:
        pass
    return None


async def is_twitter_url(url: str) -> bool:
    """检查是否是 Twitter URL

    Args:
        url: 要检查的 URL

    Returns:
        是否是 Twitter URL
    """
    pattern = r"((?:https?:)?//)?(?:www.)?twitter.com/(?:(?:\w)*#!/)?(?:pages/)?(?:[\w-]*/)*(?:[\w-]*)"
    return bool(re.match(pattern, url))


async def generate_twitter_iframe(url: str) -> Optional[str]:
    """生成 Twitter 嵌入代码

    Args:
        url: Twitter URL

    Returns:
        嵌入代码，如果生成失败则返回 None
    """
    try:
        endpoint = "https://publish.twitter.com/oembed?url="
        response = requests.get(endpoint + url, headers={"User-Agent": "Mozilla/5.0"})

        if response.status_code == 200:
            data = response.json()
            src_code = urllib.parse.quote(data["html"])
            return f'<iframe style="border:none;" width="550" height="400" data-tweet-url="{url}" src="data:text/html;charset=utf-8,{src_code}"></iframe>'

    except Exception:
        pass
    return None
