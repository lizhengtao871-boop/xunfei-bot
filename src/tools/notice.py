from src.agent.tool_registry import register_tool


@register_tool(
    name="send_notice",
    description="发送通知公告到企业微信群。此操作需要用户确认才会执行。",
    parameters={
        "type": "object",
        "properties": {
            "content": {"type": "string", "description": "通知内容（Markdown格式）"},
            "mention_all": {"type": "boolean", "description": "是否@所有人", "default": False},
        },
        "required": ["content"],
    },
)
def send_notice(content: str, mention_all: bool = False) -> str:
    try:
        from src.wx_gateway.sender import send_markdown
        result = send_markdown(content)
        if result:
            return "通知已发送" + (" (@所有人)" if mention_all else "")
        return "通知发送失败，请稍后重试。"
    except ImportError:
        return "企微网关尚未就绪，无法发送。请通过其他方式发送通知。"
