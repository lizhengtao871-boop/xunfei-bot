import time
import random
import string
from fastapi import APIRouter, Query, Request
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


@router.post("/callback")
async def receive_message(request: Request):
    timestamp = str(int(time.time()))
    nonce = _random_str()

    body = await request.body()
    root = ET.fromstring(body)
    encrypted = root.find("Encrypt")
    if encrypted is None or encrypted.text is None:
        return PlainTextResponse("")

    plain = wx_crypt.decrypt(encrypted.text)
    msg_root = ET.fromstring(plain)
    msg_type = msg_root.find("MsgType")
    content_el = msg_root.find("Content")
    from_el = msg_root.find("From")
    name_el = msg_root.find("Name")

    if msg_type is not None and msg_type.text == "text" and content_el is not None:
        text = content_el.text or ""
        user_name = (name_el.text if name_el is not None else "") or (from_el.text if from_el is not None else "未知")
        reply = process_message(text, user_name)

        if reply:
            from src.wx_gateway.sender import send_markdown
            send_markdown(reply)

    return PlainTextResponse("")
