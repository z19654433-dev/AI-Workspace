from tools import registry


@registry.register(description="查询指定城市的天气情况，当用户询问天气时调用")
def get_weather(city: str) -> str:
    """查询指定城市的天气。"""
    weather_data = {
        "河南": "今天河南天气晴，温度30℃",
        "北京": "今天北京多云，温度28℃",
        "上海": "今天上海小雨，温度26℃",
    }
    return weather_data.get(city, "暂时没有这个城市的天气信息")
