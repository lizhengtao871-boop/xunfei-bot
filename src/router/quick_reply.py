import re
from typing import Callable

_handlers: list[tuple[re.Pattern, Callable]] = []


def register_handler(pattern: str):
    def decorator(func: Callable):
        _handlers.append((re.compile(pattern), func))
        return func
    return decorator


def match_quick_reply(text: str) -> str | None:
    for pattern, handler in _handlers:
        m = pattern.match(text.strip())
        if m:
            return handler(**m.groupdict())
    return None


@register_handler(r"^(帮助|help|菜单|功能)$")
def help_reply() -> str:
    return """**讯飞协会助手 功能菜单**

📋 **任务管理** — "查看任务" / "创建任务" / "完成任务 [ID]"
👥 **成员查询** — "技术部有哪些人" / "查成员 [姓名]"
📁 **项目查看** — "项目列表" / "内部项目" / "外部项目"
📅 **活动查询** — "近期活动" / "本月会议"
📢 **发送通知** — "@bot 发通知" (需确认)
📊 **生成报告** — "生成月度报告"
🔍 **知识查询** — "协会的规章制度" / "换届流程"
"""


@register_handler(r"^(你好|hi|hello|在吗)")
def greet_reply() -> str:
    return "你好！我是讯飞协会管理助手，输入「帮助」查看我支持的功能。"


@register_handler(r"^(谢谢|感谢|thanks|3Q)")
def thanks_reply() -> str:
    return "不客气！有问题随时找我。"
