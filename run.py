# pip install zhipuai 请先在终端进行安装

import sys
from zhipuai import ZhipuAI

client = ZhipuAI(api_key="83c46d602c524ba59abda672915c3154.RhmfBAnZ054E1Lg6")

# 定义对话历史列表
dialogue_history = [
    {
        "role": "system",
        "content": "你是一个乐于解答各种问题的助手，你的任务是为用户提供专业、准确、有见地的建议。"
    }
]

# 函数：发送消息并获取响应
def send_message(message):
    dialogue_history.append({"role": "user", "content": message})
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=dialogue_history,
        top_p=0.7,
        temperature=0.95,
        max_tokens=1024,
        stream=True
    )
    assistant_response = ""
    for chunk in response:
        chunk_content = chunk.choices[0].delta.content
        sys.stdout.write(chunk_content)
        assistant_response += chunk_content
    dialogue_history.append({"role": "assistant", "content": assistant_response})

# 主循环：实现多轮对话
while True:
    user_input = input("用户：")
    if user_input.lower() == '退出':
        break
    sys.stdout.write("助手：")
    send_message(user_input)
    sys.stdout.write("\n\n")  # 在助手响应完成后添加换行符
