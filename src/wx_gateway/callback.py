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
    import sys
    try:
        reply = process_message(text, user_name)
        if reply:
            # Truncate to fit WeChat Work limits (text: 2048 bytes, markdown: 4096 bytes)
            reply_bytes = reply.encode("utf-8")
            if len(reply_bytes) > 4000:
                reply = reply_bytes[:4000].decode("utf-8", errors="replace") + "\n\n...（内容过长已截断）"

            from src.wx_gateway.sender import send_markdown
            ok = send_markdown(reply, touser=user_id)
            if not ok:
                # Fallback to text
                from src.wx_gateway.sender import send_text
                text_reply = reply_bytes[:1900].decode("utf-8", errors="replace")
                send_text(text_reply, touser=user_id)
            print(f"[callback] reply sent: {ok}, length: {len(reply)}", file=sys.stderr)
    except Exception as e:
        print(f"[callback] ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()


@router.post("/callback")
async def receive_message(request: Request):
    import sys
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
        print(f"[callback] received: {text[:100]} from {user_id}", file=sys.stderr)

        # Process in thread so callback returns within 5s timeout
        import threading
        t = threading.Thread(target=_process_and_reply, args=(text, user_id, user_name), daemon=True)
        t.start()

    return PlainTextResponse("")
