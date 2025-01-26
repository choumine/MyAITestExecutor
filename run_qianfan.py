import json
import re
import time
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

def generate_json_list(system_content: str, user_content: str) -> dict:
    client = Qianfan(
        # 方式一：使用安全认证AK/SK鉴权
        # 替换下列示例中参数，安全认证Access Key替换your_iam_ak，Secret Key替换your_iam_sk，如何获取请查看<url id="cuaui04r4djutili84s0" type="url" status="parsed" title="如何获取AKSK - 相关参考Reference | 百度智能云文档" wc="1709"><url id="" type="url" status="" title="" wc=""><url id="" type="url" status="" title="" wc=""><url id="" type="url" status="" title="" wc="">https://cloud.baidu.com/doc/Reference/s/9jwvz2egb</url></url></url></url>
        # access_key="your_iam_ak",
        # secret_key="your_iam_sk",
        # app_id="", # 选填，不填写则使用默认appid

        # 方式二：使用API Key值鉴权
        # 替换下列示例中参数，将your_APIKey替换为真实值，如何获取API Key请查看<url id="cuaui04r4djutili84sg" type="url" status="parsed" title="认证鉴权 - ModelBuilder" wc="8172"><url id="" type="url" status="" title="" wc=""><url id="" type="url" status="" title="" wc=""><url id="" type="url" status="" title="" wc="">https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um2wxbaps#步骤二-获取api-key或bearertoken值</url></url></url></url>
        # api_key="your_APIKey"
        # app_id="", # 选填，不填写则使用默认appid
    )

    max_attempts = 5  # 最大尝试次数
    attempt = 0
    while attempt < max_attempts:
        try:
            completion = client.chat.completions.create(
                model="ernie-speed-128k",  # 指定特定模型
                messages=[
                    {'role': 'system', 'content': system_content},
                    {'role': 'user', 'content': user_content}
                ]
            )

            result = completion.choices[0].message.content

            # 使用正则表达式提取JSON部分
            json_match = re.search(r'\{.*\}', result)
            if json_match:
                json_data = json.loads(json_match.group())
                return json_data
            else:
                print("No JSON found, retrying...")
        except Exception as e:
            print(f"Error occurred: {e}, retrying...")
        attempt += 1
        time.sleep(1)  # 在每次重试时增加1秒延迟

    print("Failed to get valid JSON after multiple attempts")
    return {}

# 示例调用
system_input = "你是一个手机界面测试用例分析程序。接下来我会说一些测试用例的描述，你能够分析出用例描述的界面按键，并输出示例指定的json格式结果。注意：1.用例描述中可能包含*（星号）等特殊符号，这些符号不是Markdown语法符号，不能遗漏。2.仅输出json，不要其他内容。示例：用例描述：输入*#*#8100#*#*。输出：{'key_list':[{'key':'*'},{'key':'#'},{'key':'*'},{'key':'#'},{'key':'8'},{'key':'1'},{'key':'0'},{'key':'0'},{'key':'#'},{'key':'*'},{'key':'#'},{'key':'*'}]}"
user_input = "输入*#06#"
key_result = generate_json_list(system_input, user_input)
print("Initial key_result:", key_result)

# 修改后的 hierarchy_input 赋值逻辑
hierarchy_input = f"你是一个手机界面hierarchy分析程序，这是当前手机界面的hierarchy。{get_hierarchy_json()}。接下来我会输入一些界面按键的信息，你要输出对应json格式的Xpath信息。举例：输入：按键'*'。输出：{{'xpath': '//*[@resource-id='com.android.contacts:id/star']'}}"
# 遍历 key_result 中的 key 值
xpath_results = []
if 'key_list' in key_result:
    for key_info in key_result['key_list']:
        key = key_info['key']
        # 构造新的 user_input
        new_user_input = f"按键'{key}'"
        # 调用 generate_json_list 函数
        xpath_result = generate_json_list(hierarchy_input, new_user_input)
        xpath_results.append(xpath_result)
        print(f"XPath result for key '{key}':", xpath_result)
else:
    print("No key_list found in key_result")

# 遍历 xpath_results 并执行点击操作
for xpath_result in xpath_results:
    if 'xpath' in xpath_result:
        xpath_str = xpath_result['xpath']
        click_result = click_element_by_xpath(xpath_str)
        print(f"Clicked element with XPath '{xpath_str}':", click_result)
    else:
        print("No valid XPath found in result:", xpath_result)