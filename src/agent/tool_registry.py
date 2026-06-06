from typing import Callable, Any

_tools: dict[str, Callable] = {}
_tool_schemas: list[dict] = []


def register_tool(name: str, description: str, parameters: dict):
    def decorator(func: Callable):
        _tools[name] = func
        _tool_schemas.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            },
        })
        return func
    return decorator


def get_tool_schemas() -> list[dict]:
    return _tool_schemas


def execute_tool(name: str, arguments: dict) -> Any:
    func = _tools.get(name)
    if not func:
        return {"error": f"未知工具: {name}"}
    try:
        return func(**arguments)
    except Exception as e:
        return {"error": f"工具执行失败: {e}"}


def list_tools() -> list[str]:
    return list(_tools.keys())
