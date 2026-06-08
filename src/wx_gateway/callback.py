import random
import string
import sys
from fastapi import APIRouter, Query, Request
from fastapi.responses import PlainTextResponse
import xml.etree.ElementTree as ET
from src.wx_gateway.crypto import WXBizMsgCrypt

router = APIRouter(prefix="/wx", tags=["企业微信"])
wx_crypt = WXBizMsgCrypt()


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


@router.post("/callback")
async def receive_message(request: Request):
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

        # Enqueue for background worker to process
        from src.main import msg_queue
        msg_queue.put((text, user_id, user_name))

    return PlainTextResponse("")
