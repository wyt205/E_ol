"""
AI 相关的路由接口
前端通过这些接口调用 AI 功能
"""
from fastapi import APIRouter
from pydantic import BaseModel
from app.ai_service import explain_word, generate_examples, chat_about_word

# 创建路由器
router = APIRouter(
    prefix="/api/ai",    # 所有接口以 /api/ai 开头
    tags=["ai"]          # API 文档中的分组标签
)


# ===== 请求体数据格式定义 =====
class ExplainRequest(BaseModel):
    """单词解释请求"""
    word: str        # 英文单词
    meaning: str     # 单词释义


class ExamplesRequest(BaseModel):
    """生成例句请求"""
    word: str        # 英文单词
    meaning: str     # 单词释义


class ChatRequest(BaseModel):
    """自由问答请求"""
    word: str        # 当前学习的单词
    meaning: str     # 单词释义
    question: str    # 用户输入的问题


@router.post("/explain")
def api_explain_word(req: ExplainRequest):
    """
    单词详细解释接口
    返回：词根词缀、用法、近义词、记忆技巧
    """
    answer = explain_word(req.word, req.meaning)
    return {"answer": answer}


@router.post("/examples")
def api_generate_examples(req: ExamplesRequest):
    """
    生成例句接口
    返回：3个不同场景的例句（附翻译）
    """
    answer = generate_examples(req.word, req.meaning)
    return {"answer": answer}


@router.post("/chat")
def api_chat_about_word(req: ChatRequest):
    """
    AI 问答接口
    用户针对某个单词提问，AI 回答
    """
    answer = chat_about_word(req.word, req.meaning, req.question)
    return {"answer": answer}
