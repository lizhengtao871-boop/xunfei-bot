import httpx
import time
from src.config import config

_token_cache: dict = {}

WX_API_BASE = "https://qyapi.weixin.qq.com/cgi-bin"


def _get_access_token() -> str:
    if _token_cache.get("token") and _token_cache.get("expires", 0) > time.time():
        return _token_cache["token"]

    url = f"{WX_API_BASE}/gettoken"
    params = {"corpid": config.WX_CORP_ID, "corpsecret": config.WX_AGENT_SECRET}
    resp = httpx.get(url, params=params, timeout=10)
    data = resp.json()
    if data.get("errcode") != 0:
        raise Exception(f"获取 access_token 失败: {data}")
    _token_cache["token"] = data["access_token"]
    _token_cache["expires"] = time.time() + data["expires_in"] - 300
    return data["access_token"]


def _send_message(msgtype: str, content: dict, touser: str = "@all") -> bool:
    token = _get_access_token()
    url = f"{WX_API_BASE}/message/send"
    body = {
        "touser": touser,
        "msgtype": msgtype,
        "agentid": int(config.WX_AGENT_ID),
        msgtype: content,
    }
    resp = httpx.post(url, params={"access_token": token}, json=body, timeout=10)
    return resp.json().get("errcode") == 0


def send_text(content: str, touser: str = "@all") -> bool:
    return _send_message("text", {"content": content}, touser)


def send_markdown(content: str, touser: str = "@all") -> bool:
    return _send_message("markdown", {"content": content}, touser)
