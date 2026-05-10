import requests
import json
from app.config import settings


def _build_client():
    """使用 requests 替代 OpenAI SDK，避免 httpx 在 Windows 上的兼容问题"""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    })
    return session


_session = None


def _get_session():
    global _session
    if _session is None:
        _session = _build_client()
    return _session


def call_llm(messages, temperature=0.1, max_tokens=1024, response_format=None, **kwargs):
    """通用 LLM 调用，支持 JSON 输出模式和扩展参数（tools 等）"""
    session = _get_session()
    base = settings.llm_base_url.rstrip("/")
    url = f"{base}/chat/completions"

    body = {
        "model": settings.llm_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    if response_format:
        body["response_format"] = response_format
    body.update(kwargs)

    try:
        resp = session.post(url, json=body, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]
    except requests.exceptions.Timeout:
        raise Exception("LLM 请求超时，请检查网络连接")
    except requests.exceptions.RequestException as e:
        raise Exception(f"LLM 请求失败: {str(e)}")
