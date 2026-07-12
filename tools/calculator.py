def calculate(expression):

    try:
        result = eval(expression)
        return f"计算结果：{result}"

    except Exception:
        return "无法计算这个表达式"