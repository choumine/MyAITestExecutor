import json
import re
from qianfan import Qianfan

def generate_key_list(user_content: str) -> dict:
    client = Qianfan(
        # 方式一：使用安全认证AK/SK鉴权
        # 替换下列示例中参数，安全认证Access Key替换your_iam_ak，Secret Key替换your_iam_sk，如何获取请查看<url id="cuaui04r4djutili84s0" type="url" status="parsed" title="如何获取AKSK - 相关参考Reference | 百度智能云文档" wc="1709">https://cloud.baidu.com/doc/Reference/s/9jwvz2egb</url>
        # access_key="your_iam_ak",
        # secret_key="your_iam_sk",
        # app_id="", # 选填，不填写则使用默认appid

        # 方式二：使用API Key值鉴权
        # 替换下列示例中参数，将your_APIKey替换为真实值，如何获取API Key请查看<url id="cuaui04r4djutili84sg" type="url" status="parsed" title="认证鉴权 - ModelBuilder" wc="8172">https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um2wxbaps#步骤二-获取api-key或bearertoken值</url>
        # api_key="your_APIKey"
        # app_id="", # 选填，不填写则使用默认appid
    )

    completion = client.chat.completions.create(
        model="ernie-speed-128k",  # 指定特定模型
        messages=[
            # 也可以不设置system字段
            {
                'role': 'system',
                'content': '你是一个手机界面测试用例分析程序。接下来我会说一些测试用例的描述，你能够分析出用例描述的界面按键，并输出示例指定的json格式结果。注意：1.用例描述中可能包含*（星号）等特殊符号，这些符号不是Markdown语法符号，不能遗漏。2.仅输出json，不要其他内容。示例：用例描述：输入*#*#8100#*#*。输出：{"key_list":[{"key":"*"},{"key":"#"},{"key":"*"},{"key":"#"},{"key":"8"},{"key":"1"},{"key":"0"},{"key":"0"},{"key":"#"},{"key":"*"},{"key":"#"},{"key":"*"}]}'
            },
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
        print("No JSON found")
        return {}


# 示例调用
user_input = "输入*#800#"
json_result = generate_key_list(user_input)
print(json_result)