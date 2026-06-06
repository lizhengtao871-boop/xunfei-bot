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
    to_user = msg_root.find("ToUserName")
    agent_type = msg_root.find("AgentType")

    reply_text = ""
    if msg_type is not None and msg_type.text == "text" and content_el is not None:
        text = content_el.text or ""
        user_id = from_user.text if from_user is not None else ""
        user_name = user_id or "未知"
        reply_text = process_message(text, user_name)

        # Also try active send (may fail due to IP restriction, that's OK)
        try:
            from src.wx_gateway.sender import send_markdown
            send_markdown(reply_text, touser=user_id)
        except Exception:
            pass

    # Passive reply (encrypted in response XML) — bypasses IP whitelist
    if reply_text and from_user is not None:
        ts = str(int(time.time()))
        nc = _random_str()
        reply_xml = (
            f"<xml>"
            f"<ToUserName><![CDATA[{from_user.text}]]></ToUserName>"
            f"<FromUserName><![CDATA[{to_user.text if to_user is not None else ''}]]></FromUserName>"
            f"<CreateTime>{ts}</CreateTime>"
            f"<MsgType><![CDATA[text]]></MsgType>"
            f"<Content><![CDATA[{reply_text}]]></Content>"
            f"</xml>"
        )
        encrypted_xml, signature = wx_crypt.sign_encrypt(reply_xml, ts, nc)
        return Response(
            content=f"<xml><Encrypt><![CDATA[{encrypted_xml}]]></Encrypt><MsgSignature><![CDATA[{signature}]]></MsgSignature><TimeStamp>{ts}</TimeStamp><Nonce><![CDATA[{nc}]]></Nonce></xml>",
            media_type="application/xml",
        )

    return PlainTextResponse("")
