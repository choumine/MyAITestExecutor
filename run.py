# pip install zhipuai 请先在终端进行安装

import sys
import os
import logging
from zhipuai import ZhipuAI

# 配置 logging
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为 INFO
    format="%(asctime)s - %(levelname)s - %(message)s",  # 设置日志格式
    handlers=[
        logging.StreamHandler(sys.stdout)  # 将日志输出到控制台
    ]
)
logger = logging.getLogger(__name__)

# 从环境变量中读取API密钥
api_key = os.getenv("ZHIPUAI_API_KEY")
if not api_key:
    raise ValueError("请设置环境变量 ZHIPUAI_API_KEY")

# 初始化ZhipuAI客户端
client = ZhipuAI(api_key=api_key)

# 定义对话历史列表，初始包含系统消息
dialogue_history = [
    {
        "role": "system",
        "content": "你是一个乐于解答各种问题的助手，你的任务是为用户提供专业、准确、有见地的建议。"
    }
]

# 设置最大对话历史长度
MAX_HISTORY_LENGTH = 10

# 函数：打印 dialogue_history 的变化
def log_dialogue_history():
    logger.info("当前对话历史：")
    for entry in dialogue_history:
        logger.info(f"{entry['role']}: {entry['content']}")
    logger.info("")  # 添加空行分隔

# 函数：获取API响应
def get_api_response(messages):
    return client.chat.completions.create(
        model="glm-4-flash",
        messages=messages,
        top_p=0.7,
        temperature=0.95,
        max_tokens=1024,
        stream=True
    )

# 函数：处理API响应
def process_response(response):
    assistant_response = ""
    for chunk in response:
        chunk_content = chunk.choices[0].delta.content
        print(chunk_content, end="", flush=True)  # 实时输出助手响应
        assistant_response += chunk_content
    print("\n")  # 在助手响应完成后添加换行符
    return assistant_response

# 函数：发送消息并获取响应
def send_message(message):
    global dialogue_history
    dialogue_history.append({"role": "user", "content": message})

    # 如果对话历史超过最大长度，删除最早的对话记录（保留系统消息）
    if len(dialogue_history) > MAX_HISTORY_LENGTH:
        dialogue_history.pop(1)

    try:
        response = get_api_response(dialogue_history)
        assistant_response = process_response(response)
        dialogue_history.append({"role": "assistant", "content": assistant_response})

        # 记录 dialogue_history 的变化
        log_dialogue_history()
    except Exception as e:
        logger.error(f"发生错误: {e}", exc_info=True)

# 主循环：实现多轮对话
while True:
    user_input = input("用户：")

    # 检查用户输入是否为退出命令
    if user_input.lower() == '退出':
        print("对话已结束，感谢使用！")
        break

    # 检查用户输入是否为空
    if not user_input.strip():
        print("输入不能为空，请重新输入。")
        continue

    # 检查用户输入是否为修改系统角色的命令
    if user_input.lower() == '修改系统角色':
        new_system_content = input("请输入新的系统角色内容：")
        if new_system_content.strip():
            dialogue_history[0]["content"] = new_system_content
            print("系统角色内容已更新。")
            continue
        else:
            print("输入不能为空，请重新输入。")
            continue

    # 发送用户输入并获取助手响应
    print("助手：", end="")
    send_message(user_input)