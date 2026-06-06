import json
from src.router.quick_reply import match_quick_reply
from src.agent.core import llm
from src.agent.prompt import SYSTEM_PROMPT
from src.agent.tool_registry import get_tool_schemas, execute_tool
from src.tools import auto_import_tools

auto_import_tools()


def process_message(text: str, user_name: str = "") -> str:
    quick = match_quick_reply(text)
    if quick:
        return quick

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"[用户: {user_name}]\n{text}"},
    ]

    tools = get_tool_schemas()
    response = llm.chat(messages, tools=tools if tools else None)

    tool_calls = response.get("tool_calls", [])
    if tool_calls:
        openai_tool_calls = [
            {
                "id": tc["id"],
                "type": "function",
                "function": {
                    "name": tc["name"],
                    "arguments": json.dumps(tc["arguments"], ensure_ascii=False),
                },
            }
            for tc in tool_calls
        ]
        messages.append({
            "role": "assistant",
            "content": response.get("content") or "",
            "tool_calls": openai_tool_calls,
        })
        for tc in tool_calls:
            result = execute_tool(tc["name"], tc["arguments"])
            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": json.dumps(result, ensure_ascii=False),
            })
        final = llm.chat(messages)
        return final.get("content", "抱歉，处理过程中出现了问题。")
    else:
        return response.get("content", "")
