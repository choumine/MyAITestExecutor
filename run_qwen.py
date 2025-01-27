'''
# 文本输入
import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
completion = client.chat.completions.create(
    model="qwen2.5-3b-instruct",
    # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    messages=[
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': '你是谁？'}],
)

print(completion.model_dump_json())
'''

'''
# 流式输出
import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
completion = client.chat.completions.create(
    model="qwen2.5-3b-instruct",
    messages=[{'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': '你是谁？'}],
    stream=True,
    stream_options={"include_usage": True}
    )
for chunk in completion:
    print(chunk.model_dump_json())
'''

'''
# 工具调用
import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope SDK的base_url
)

tools = [
    # 工具1 获取当前时刻的时间
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "当你想知道现在的时间时非常有用。",
            "parameters": {}  # 因为获取当前时间无需输入参数，因此parameters为空字典
        }
    },
    # 工具2 获取指定城市的天气
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "当你想查询指定城市的天气时非常有用。",
            "parameters": {
                "type": "object",
                "properties": {
                    # 查询天气时需要提供位置，因此参数设置为location
                    "location": {
                        "type": "string",
                        "description": "城市或县区，比如北京市、杭州市、余杭区等。"
                    }
                },
                "required": ["location"]
            }
        }
    }
]
messages = [{"role": "user", "content": "杭州天气怎么样"}]
completion = client.chat.completions.create(
    model="qwen2.5-3b-instruct",
    messages=messages,
    tools=tools
)

print(completion.model_dump_json())
'''

import os
import json
from datetime import datetime
from openai import OpenAI
import subprocess
from typing import List

# 初始化OpenAI客户端
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 获取设备
def get_adb_devices() -> List[str]:
    """
    执行 adb devices 命令，返回已连接且状态为 'device' 的 Android 设备序列号列表
    （若没有可用设备或命令执行失败，返回空列表）
    """
    try:
        # 执行 adb devices 命令并捕获输出
        result = subprocess.check_output(
            ["adb", "devices"],
            stderr=subprocess.STDOUT,
            text=True
        )

        # 解析输出内容
        devices = []
        lines = result.strip().split('\n')
        if len(lines) < 2:
            return devices  # 无设备连接

        # 从第二行开始解析设备信息（跳过标题行）
        for line in lines[1:]:
            parts = line.strip().split()
            # 仅保留状态为 'device' 的设备
            if len(parts) >= 2 and parts[1] == 'device':
                devices.append(parts[0])

        return devices

    except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
        print(f"Error executing adb: {str(e)}")
        return []


# 定义工具列表
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "当你想知道现在的时间时非常有用。",
            "parameters": {}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "当你想查询指定城市的天气时非常有用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市或县区，比如北京市、杭州市、余杭区等。"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_adb_devices",
            "description": "执行 adb devices 命令，返回已连接且状态为 'device' 的 Android 设备序列号列表。",
            "parameters": {}
        }
    }
]


# 模拟天气查询工具
def get_current_weather(location):
    return f"{location}今天是雨天。"


# 查询当前时间的工具
def get_current_time():
    current_datetime = datetime.now()
    formatted_time = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    return f"当前时间：{formatted_time}。"


# 封装模型响应函数
def get_response(messages):
    try:
        completion = client.chat.completions.create(
            model="qwen2.5-3b-instruct",
            messages=messages,
            tools=tools
        )
        return completion.model_dump()
    except Exception as e:
        print(f"调用模型时发生错误: {e}")
        return None


def call_with_messages():
    messages = [
        {
            "content": input('请输入：'),
            "role": "user"
        }
    ]
    print("-" * 60)
    i = 1

    first_response = get_response(messages)
    if not first_response:
        return

    assistant_output = first_response['choices'][0]['message']
    print(f"\n第{i}轮大模型输出信息：{first_response}\n")

    if assistant_output['content'] is None:
        assistant_output['content'] = ""
    messages.append(assistant_output)

    if assistant_output['tool_calls'] is None:
        print(f"无需调用工具，我可以直接回复：{assistant_output['content']}")
        return

    while assistant_output['tool_calls'] is not None:
        tool_name = assistant_output['tool_calls'][0]['function']['name']
        tool_info = {"name": tool_name, "role": "tool"}

        if tool_name == 'get_current_weather':
            try:
                location = json.loads(assistant_output['tool_calls'][0]['function']['arguments'])['location']
                tool_info['content'] = get_current_weather(location)
            except json.JSONDecodeError as e:
                print(f"解析工具参数时发生错误: {e}")
                return
        elif tool_name == 'get_current_time':
            tool_info['content'] = get_current_time()
        elif tool_name == 'get_adb_devices':
            devices = get_adb_devices()
            if devices:
                device_str = ", ".join(devices)
                tool_info['content'] = f"已连接的 Android 设备序列号：{device_str}"
            else:
                tool_info['content'] = "没有检测到已连接的 Android 设备。"

        print(f"工具输出信息：{tool_info['content']}\n")
        print("-" * 60)
        messages.append(tool_info)

        assistant_output = get_response(messages)
        if not assistant_output:
            return

        assistant_output = assistant_output['choices'][0]['message']
        if assistant_output['content'] is None:
            assistant_output['content'] = ""
        messages.append(assistant_output)
        i += 1
        print(f"第{i}轮大模型输出信息：{assistant_output}\n")

    print(f"最终答案：{assistant_output['content']}")


if __name__ == '__main__':
    call_with_messages()