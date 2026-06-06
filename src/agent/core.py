import json
import time
from typing import Any
from openai import OpenAI
from src.config import config

_client = OpenAI(
    api_key=config.DEEPSEEK_API_KEY,
    base_url=config.DEEPSEEK_BASE_URL,
)


class LLM:
    def __init__(self, model: str | None = None):
        self.model = model or config.DEEPSEEK_MODEL

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        tool_choice: str = "auto",
    ) -> dict[str, Any]:
        kwargs: dict = dict(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
        )
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice

        for attempt in range(config.MAX_RETRIES):
            try:
                resp = _client.chat.completions.create(**kwargs)
                choice = resp.choices[0]
                result: dict[str, Any] = {"content": choice.message.content}
                if choice.message.tool_calls:
                    tool_calls = []
                    for tc in choice.message.tool_calls:
                        try:
                            args = json.loads(tc.function.arguments)
                        except (json.JSONDecodeError, TypeError):
                            args = {}
                        tool_calls.append({
                            "id": tc.id,
                            "name": tc.function.name,
                            "arguments": args,
                        })
                    result["tool_calls"] = tool_calls
                return result
            except Exception as e:
                if attempt == config.MAX_RETRIES - 1:
                    return {"content": f"[错误] 调用 AI 服务失败: {e}"}
                time.sleep(2 ** attempt)
        return {"content": "[错误] 未知错误"}


llm = LLM()
