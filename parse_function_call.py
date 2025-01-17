import json
from zhipuai import ZhipuAI

client = ZhipuAI(api_key="83c46d602c524ba59abda672915c3154.RhmfBAnZ054E1Lg6")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_flight_number",
            "description": "根据始发地、目的地和日期，查询对应日期的航班号",
            "parameters": {
                "type": "object",
                "properties": {
                    "departure": {
                        "description": "出发地",
                        "type": "string"
                    },
                    "destination": {
                        "description": "目的地",
                        "type": "string"
                    },
                    "date": {
                        "description": "日期",
                        "type": "string",
                    }
                },
                "required": ["departure", "destination", "date"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_ticket_price",
            "description": "查询某航班在某日的票价",
            "parameters": {
                "type": "object",
                "properties": {
                    "flight_number": {
                        "description": "航班号",
                        "type": "string"
                    },
                    "date": {
                        "description": "日期",
                        "type": "string",
                    }
                },
                "required": ["flight_number", "date"]
            },
        }
    },
]

def get_flight_number(date:str , departure:str , destination:str):
    flight_number = {
        "北京":{
            "上海" : "1234",
            "广州" : "9527",
        },
        "上海":{
            "北京" : "1233",
            "广州" : "8123",
        }
    }
    return { "flight_number":flight_number[departure][destination] }

def get_ticket_price(date:str , flight_number:str):
    return {"ticket_price": "1000"}


# 解析函数调用并执行
def parse_function_call(model_response,messages):
    # 处理函数调用结果，根据模型返回参数，调用对应的函数。
    # 调用函数返回结果后构造tool message，再次调用模型，将函数结果输入模型
    # 模型会将函数调用结果以自然语言格式返回给用户。
    if model_response.choices[0].message.tool_calls:
        tool_call = model_response.choices[0].message.tool_calls[0]
        args = tool_call.function.arguments
        function_result = {}
        if tool_call.function.name == "get_flight_number":
            function_result = get_flight_number(**json.loads(args))
        if tool_call.function.name == "get_ticket_price":
            function_result = get_ticket_price(**json.loads(args))
        messages.append({
            "role": "tool",
            "content": f"{json.dumps(function_result)}",
            "tool_call_id":tool_call.id
        })
        response = client.chat.completions.create(
            model="glm-4-flash",  # 填写需要调用的模型名称
            messages=messages,
            tools=tools,
        )
        print(response.choices[0].message)
        messages.append(response.choices[0].message.model_dump())
    else:
        print(model_response.choices[0].message)
        messages.append(model_response.choices[0].message.model_dump())


# 主函数
def main():
    messages = [{"role": "user", "content": "帮我查询1月23日，北京到广州的航班"}]
    # 用户询问航班号
    response = client.chat.completions.create(model="glm-4-flash", messages=messages, tools=tools)
    parse_function_call(response, messages)

    # 假设用户接着询问票价
    messages.append({"role": "user", "content": "请告诉我这趟航班的票价"})
    # 第二次调用，查询票价
    response = client.chat.completions.create(model="glm-4-flash", messages=messages, tools=tools)
    parse_function_call(response, messages)

    # 假设用户问无关问题
    messages.append({"role": "user", "content": "讲一个山西历史故事"})
    response = client.chat.completions.create(model="glm-4-flash", messages=messages, tools=tools)
    parse_function_call(response, messages)

    # 打印所有消息
    for msg in messages:
        print(f"{msg['role']}: {msg['content']}")


if __name__ == "__main__":
    main()
