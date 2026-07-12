def get_weather(city):

    weather_data = {
        "河南": "今天河南天气晴，温度30℃",
        "北京": "今天北京多云，温度28℃",
        "上海": "今天上海小雨，温度26℃"
    }

    return weather_data.get(
        city,
        "暂时没有这个城市的天气信息"
    )