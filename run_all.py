import json
import re
from qianfan import Qianfan
import uiautomator2 as u2

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


def extract_json_from_string(input_str):
    """
    从字符串中提取 JSON 数据并解析为 Python 字典。

    :param input_str: 包含 JSON 数据的字符串
    :return: 解析后的字典（如果成功），否则返回 None
    """
    # 使用正则表达式提取 JSON 部分
    match = re.search(r'\{.*\}', input_str, re.DOTALL)

    if match:
        json_str = match.group(0)  # 提取匹配的 JSON 部分
        try:
            # 尝试解析 JSON
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError:
            print("提取的 JSON 数据格式无效")
            return None
    else:
        print("未找到 JSON 数据")
        return None

system_input = ("你是一个手机界面测试用例分析程序。"
                "接下来我会说一些测试用例的描述，你能够分析出用例描述的界面按键，并输出示例指定的json格式结果。"
                "注意："
                "1.用例描述中可能包含*（星号）等特殊符号，这些符号不是Markdown语法符号，不能遗漏。"
                "2.仅输出json，不要其他内容。"
                "示例："
                "用例描述：输入*#*#8100#*#*。"
                "输出：{'key_list':[{'key':'*'},{'key':'#'},{'key':'*'},{'key':'#'},{'key':'8'},{'key':'1'},{'key':'0'},{'key':'0'},{'key':'#'},{'key':'*'},{'key':'#'},{'key':'*'}]}")
user_input = "输入*#06#"

client = Qianfan()

# 初始化对话历史
messages = [
    {'role': 'system', 'content': system_input}]

# 将用户输入添加到对话历史中
messages.append({'role': 'user', 'content': user_input})

# 发送请求并获取响应
completion = client.chat.completions.create(
    model="ernie-speed-128k",
    messages=messages
)

# 获取模型的回复
assistant_reply = completion.choices[0].message.content

print(assistant_reply)

assistant_reply = extract_json_from_string(assistant_reply)

xpath_input = []
if 'key_list' in assistant_reply:
    for key_info in assistant_reply['key_list']:
        key = key_info['key']
        # 构造新的 user_input
        new_user_input = f"按键'{key}'"
        xpath_input.append(new_user_input)
else:
    print("No key_list found in key_result")

print(xpath_input)

def get_xpath_from_key_sequence(key_sequence):
    client = Qianfan()

    # 初始化对话历史
    messages = [
        {'role': 'system', 'content': f"你是一个手机界面hierarchy分析程序，这是当前手机界面的hierarchy。"
                                      f"{get_hierarchy_json()}。"
                                      f"接下来我会输入一些界面按键的信息，你要输出对应json格式的Xpath信息。注意输出json格式正确，且不要输出其他内容。"
                                      f"举例：输入：按键'*'输出：{{'xpath': '//*[@resource-id='com.android.contacts:id/star']'}}。"}
    ]

    xpath_results = []

    for key_info in key_sequence:

        # 将用户输入添加到对话历史中
        messages.append({'role': 'user', 'content': key_info})

        # 发送请求并获取响应
        completion = client.chat.completions.create(
            model="ernie-speed-128k",
            messages=messages
        )

        # 获取模型的回复
        assistant_reply = completion.choices[0].message.content
        print(assistant_reply)

        # 将模型的回复添加到对话历史中
        messages.append({'role': 'assistant', 'content': assistant_reply})

        # 将Xpath信息添加到结果列表中
        assistant_reply = extract_json_from_string(assistant_reply)
        print(assistant_reply)
        xpath_results.append(assistant_reply)

    return xpath_results

xpath_list = get_xpath_from_key_sequence(xpath_input)
print(xpath_list)

# 遍历 xpath_results 并执行点击操作
for xpath_result in xpath_list:
    if 'xpath' in xpath_result:
        xpath_str = xpath_result['xpath']
        click_result = click_element_by_xpath(xpath_str)
        print(f"Clicked element with XPath '{xpath_str}':", click_result)
    else:
        print("No valid XPath found in result:", xpath_result)

messages = [
    {'role': 'system', 'content': f"你是一个手机界面hierarchy分析程序，这是当前手机界面的hierarchy。"
                                  f"{get_hierarchy_json()}。"
                                  f"接下来我会输入一些界面信息检查的要求，你要检查这些信息是否符合要求，输出结论PASS或者FAIL，并给出理由。"}
    ]
user_input = "请检查：1. 卡1IMEI为15位，不全为0。2. 卡2IMEI为15位，不全为0。"

# 将用户输入添加到对话历史中
messages.append({'role': 'user', 'content': user_input})

# 发送请求并获取响应
completion = client.chat.completions.create(
    model="ernie-speed-128k",
    messages=messages
)

# 获取模型的回复
assistant_reply = completion.choices[0].message.content

print(assistant_reply)
