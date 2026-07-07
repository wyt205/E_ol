"""
AI 服务模块
封装智谱 GLM-4.7-Flash 的调用逻辑
提供单词解释、例句生成、自由问答等 AI 能力
"""
from zai import ZhipuAiClient

# 初始化智谱 AI 客户端
# api_key 需要用户自行到 https://open.bigmodel.cn/ 申请
client = ZhipuAiClient(api_key="53ef144b4a074972b1a621f422af59a0.B7vlxuCREvZUnBdg")  # TODO: 替换为你的 API Key


def ask_ai(messages: list, use_thinking: bool = False) -> str:
    """
    通用 AI 调用函数
    参数：
    - messages: 对话消息列表，格式 [{"role": "user", "content": "..."}]
    - use_thinking: 是否启用深度思考模式（默认关闭，flash 模型响应快）
    返回：
    - AI 回复的文本内容
    """
    # 构造请求参数
    kwargs = {
        "model": "glm-4.7-flash",          # 免费模型，速度快
        "messages": messages,                # 对话消息
        "max_tokens": 4096,                  # 最大输出 token 数
        "temperature": 0.7                   # 控制随机性，0.7 适合教学场景
    }
    # 如果需要深度思考，添加 thinking 参数
    if use_thinking:
        kwargs["thinking"] = {"type": "enabled"}

    # 调用 API
    response = client.chat.completions.create(**kwargs)
    # 提取并返回回复文本
    return response.choices[0].message.content


def explain_word(word: str, meaning: str) -> str:
    """
    AI 详细解释单词
    包含：词根词缀、常见用法、近义词辨析、记忆技巧
    参数：
    - word: 英文单词
    - meaning: 已有释义（作为上下文提供给 AI）
    """
    messages = [
        {"role": "system", "content": "你是一位专业的英语老师，擅长用简洁易懂的方式讲解英语单词。请用中文回答。"},
        {"role": "user", "content": f"请详细解释英语单词 \"{word}\"（释义：{meaning}），包括：\n1. 词根词缀分析\n2. 常见用法和搭配\n3. 近义词辨析（列出2-3个）\n4. 实用记忆技巧\n请简洁回答，每个部分2-3句话即可。"}
    ]
    return ask_ai(messages)


def generate_examples(word: str, meaning: str) -> str:
    """
    AI 为单词生成更多例句
    参数：
    - word: 英文单词
    - meaning: 释义
    返回：
    - 3个不同场景的例句，每个附带中文翻译
    """
    messages = [
        {"role": "system", "content": "你是一位英语老师。请为用户生成地道的英语例句。"},
        {"role": "user", "content": f"请为英语单词 \"{word}\"（{meaning}）生成3个不同生活场景的例句。\n格式要求：每行一个例句，格式为「英文例句 / 中文翻译」，不要编号。"}
    ]
    return ask_ai(messages)


def chat_about_word(word: str, meaning: str, question: str) -> str:
    """
    AI 问答：用户针对某个单词提问
    参数：
    - word: 当前学习的单词
    - meaning: 单词释义
    - question: 用户的具体问题
    返回：
    - AI 的回答
    """
    messages = [
        {"role": "system", "content": f"用户正在学习英语单词 \"{word}\"（{meaning}），请你作为英语老师回答用户的问题。回答简洁，用中文。"},
        {"role": "user", "content": question}
    ]
    return ask_ai(messages)
