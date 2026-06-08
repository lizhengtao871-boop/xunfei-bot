import time
import random
import string
import threading
from fastapi import APIRouter, Query, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse, Response
import xml.etree.ElementTree as ET
from src.wx_gateway.crypto import WXBizMsgCrypt
from src.router.intent import process_message

router = APIRouter(prefix="/wx", tags=["企业微信"])
wx_crypt = WXBizMsgCrypt()


def _random_str(n: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


@router.get("/callback")
async def verify_url(
    msg_signature: str = Query(...),
    timestamp: str = Query(...),
    nonce: str = Query(...),
    echostr: str = Query(...),
):
    decrypted = wx_crypt.verify_url(msg_signature, timestamp, nonce, echostr)
    if decrypted is not None:
        return PlainTextResponse(decrypted)
    return PlainTextResponse("signature failed", status_code=403)


def _process_and_reply(text: str, user_id: str, user_name: str):
    """Process message in background and send reply via active API."""
    try:
        reply = process_message(text, user_name)
        if reply:
            from src.wx_gateway.sender import send_markdown
            send_markdown(reply, touser=user_id)
    except Exception as e:
        print(f"[callback] process error: {e}")


@router.post("/callback")
async def receive_message(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    root = ET.fromstring(body)
    encrypted = root.find("Encrypt")
    if encrypted is None or encrypted.text is None:
        return PlainTextResponse("")

    plain = wx_crypt.decrypt(encrypted.text)
    msg_root = ET.fromstring(plain)
    msg_type = msg_root.find("MsgType")
    content_el = msg_root.find("Content")
    from_user = msg_root.find("FromUserName")

    if msg_type is not None and msg_type.text == "text" and content_el is not None:
        text = content_el.text or ""
        user_id = from_user.text if from_user is not None else ""
        user_name = user_id or "未知"

        # Process in background so callback returns within 5s timeout
        background_tasks.add_task(_process_and_reply, text, user_id, user_name)

    # Always return empty immediately
    return PlainTextResponse("")
