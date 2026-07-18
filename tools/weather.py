"""天气工具：对接 wttr.in 免费 API，无需 API Key"""

from tools import registry
from utils.logger import get_logger
import httpx

logger = get_logger(__name__)

_TIMEOUT = 8.0


@registry.register(description="查询指定城市的实时天气情况，当用户询问天气时调用")
def get_weather(city: str) -> str:
    """查询指定城市的实时天气。

    Args:
        city: 城市名称，如 北京、上海、广州
    """
    if not city or not city.strip():
        return "请告诉我你想查询哪个城市的天气"

    city = city.strip()
    url = f"https://wttr.in/{city}?format=j1"
    headers = {"User-Agent": "curl/8.0"}

    try:
        with httpx.Client(timeout=_TIMEOUT, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except httpx.TimeoutException:
        logger.warning("查询天气超时: %s", city)
        return city + " 天气查询超时，请稍后重试"
    except httpx.HTTPStatusError as e:
        logger.warning("查询天气返回 %s: %s", e.response.status_code, city)
        return "查询 " + city + " 天气失败，城市名可能不正确"
    except Exception as e:
        logger.error("查询天气异常: %s", e)
        return "查询 " + city + " 天气时出错了"

    try:
        current = data["current_condition"][0]
        area = data["nearest_area"][0]["areaName"][0]["value"]

        temp = current.get("temp_C", "?")
        feels = current.get("feelsLikeC", temp)
        desc = current.get("weatherDesc", [{}])[0].get("value", "?")
        humidity = current.get("humidity", "?")
        wind = current.get("windSpeedKmph", "?")
        wind_dir = current.get("winddir16Point", "")

        lines = [
            area + " 当前天气：" + desc,
            "温度：" + str(temp) + "°C（体感 " + str(feels) + "°C）",
            "湿度：" + str(humidity) + "%",
            "风速：" + str(wind) + " km/h " + wind_dir,
        ]
        return "\n".join(lines)
    except (KeyError, IndexError, TypeError) as e:
        logger.error("解析天气数据失败: %s", e)
        return "获取 " + city + " 天气数据成功但解析失败，请重试"
