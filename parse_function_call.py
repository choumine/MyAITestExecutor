import json
import os
import logging
from zhipuai import ZhipuAI
import uiautomator2 as u2

# 初始化日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 从环境变量中读取 API 密钥
api_key = os.getenv("ZHIPUAI_API_KEY")
if not api_key:
    raise ValueError("请设置环境变量 ZHIPUAI_API_KEY")

# 初始化 ZhipuAI 客户端
client = ZhipuAI(api_key=api_key)

# 定义工具函数
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
    {
        "type": "function",
        "function": {
            "name": "click_element_by_xpath",
            "description": "根据给定的 XPath 点击元素",
            "parameters": {
                "type": "object",
                "properties": {
                    "xpath_str": {
                        "description": "XPath 字符串",
                        "type": "string"
                    }
                },
                "required": ["xpath_str"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_hierarchy_json",
            "description": "获取设备的界面层次结构信息并转换为JSON格式。如果未提供设备序列号，将使用默认连接方式。",
            "parameters": {
                "type": "object",
                "properties": {
                    "device_serial": {
                        "description": "设备序列号，可选参数",
                        "type": "string",
                        "default": ""
                    }
                },
                "required": []
            }
        }
    }
]

# 工具函数实现
def validate_flight_params(params):
    """验证航班查询参数是否完整"""
    required_fields = ["departure", "destination", "date"]
    for field in required_fields:
        if field not in params:
            raise ValueError(f"缺少必要参数: {field}")

def get_flight_number(date: str, departure: str, destination: str):
    """
    根据始发地、目的地和日期，查询对应日期的航班号。

    :param date: 日期，格式为字符串。
    :param departure: 出发地，格式为字符串。
    :param destination: 目的地，格式为字符串。
    :return: 包含航班号的字典。
    """
    validate_flight_params({"date": date, "departure": departure, "destination": destination})
    flight_number = {
        "北京": {
            "上海": "1234",
            "广州": "9527",
        },
        "上海": {
            "北京": "1233",
            "广州": "8123",
        }
    }
    return {"flight_number": flight_number[departure][destination]}

def get_ticket_price(date: str, flight_number: str):
    """
    查询某航班在某日的票价。

    :param date: 日期，格式为字符串。
    :param flight_number: 航班号，格式为字符串。
    :return: 包含票价的字典。
    """
    return {"ticket_price": "1514"}

def click_element_by_xpath(xpath_str: str):
    """
    根据给定的 XPath 点击元素。

    :param xpath_str: XPath 字符串。
    :return: 包含操作结果的字典。
    """
    try:
        device = u2.connect()  # 连接设备
        device.xpath(xpath_str).click()
        result = {
            "status": "success",
            "message": "操作成功！"
        }
    except Exception as e:
        result = {
            "status": "error",
            "message": str(e)
        }
    return result

def get_hierarchy_json(device_serial=''):
    """
    获取设备的界面层次结构信息并转换为 JSON 格式。

    :param device_serial: 设备序列号，可选参数。如果为空，则使用默认连接方式。
    :return: 包含界面层次结构信息的字典，或包含错误信息的字典。
    """
    try:
        # 连接设备
        device = u2.connect(device_serial) if device_serial else u2.connect()
        # 检查设备是否连接成功
        if not device.device_info:
            raise Exception("设备连接失败")
        # 获取设备的界面层次结构信息
        hierarchy = device.dump_hierarchy()
        # 返回层次结构信息
        return {
            "hierarchy": hierarchy
        }
    except Exception as e:
        return {
            "error": str(e)
        }

# 工具函数映射
tool_functions = {
    "get_flight_number": get_flight_number,
    "get_ticket_price": get_ticket_price,
    "click_element_by_xpath": click_element_by_xpath,
    "get_hierarchy_json": get_hierarchy_json,
}

# 解析函数调用并执行
def parse_function_call(model_response, messages):
    """
    解析模型返回的函数调用并执行相应的工具函数。

    :param model_response: 模型的响应对象。
    :param messages: 对话历史记录。
    """
    if model_response.choices[0].message.tool_calls:
        tool_call = model_response.choices[0].message.tool_calls[0]
        args = tool_call.function.arguments
        function_name = tool_call.function.name
        try:
            logging.info(f"调用函数: {function_name}，参数: {args}")
            if function_name in tool_functions:
                function_result = tool_functions[function_name](**json.loads(args))
            else:
                raise ValueError(f"未知函数：{function_name}")
        except Exception as e:
            logging.error(f"函数调用失败: {e}")
            function_result = {
                "status": "error",
                "message": str(e)
            }

        # 将函数结果添加到对话历史
        messages.append({
            "role": "tool",
            "content": json.dumps(function_result),
            "tool_call_id": tool_call.id
        })

        # 再次调用模型
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=messages,
            tools=tools,
        )
        print("助手:", response.choices[0].message.content)
        messages.append({"role": "assistant", "content": response.choices[0].message.content})
    else:
        print("助手:", model_response.choices[0].message.content)
        messages.append({"role": "assistant", "content": model_response.choices[0].message.content})

# 主函数
def main():
    """
    主函数，启动多轮对话系统。
    """
    messages = []  # 初始化对话历史
    print("欢迎使用多轮对话系统！输入 'exit' 退出。")
    while True:
        user_input = input("你: ")  # 获取用户输入
        if user_input.lower() == "exit":
            print("对话结束，再见！")
            break

        # 将用户输入添加到对话历史
        messages.append({"role": "user", "content": user_input})

        # 调用模型
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=messages,
            tools=tools,
        )

        # 解析函数调用
        parse_function_call(response, messages)

if __name__ == "__main__":
    main()
'''
欢迎使用多轮对话系统！输入 'exit' 退出。
你: 帮我查询1月23日，北京到广州的航班
助手: 1月23日，北京到广州的航班号是9527。
你: 这趟航班的票价是多少？
助手: 1月23日，航班9527的票价是1514元。
你: 点击这个Xpath："//*[@resource-id='com.android.contacts:id/one']"
助手: 操作成功！
你: 获取当前设备的界面层次结构信息
助手: 当前设备的界面层次结构信息已获取。
你: exit
对话结束，再见！
'''