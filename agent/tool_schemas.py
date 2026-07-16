# agent/tool_schemas.py

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "weather",          # 必须和 registry.py 里的 key 一致！
            "description": "查询指定城市的天气情况，当用户询问天气时调用",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如：北京、上海、河南"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",       # 必须和 registry.py 里的 key 一致！
            "description": "执行数学计算，当用户需要计算加减乘除时调用",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，例如：1+1 或 12345*678"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]