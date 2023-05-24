from app.Message.MessageHandler import MessageHandler

@MessageHandler.register
class BaseMessage:
    support_msgtypes: list = []
    msgdata: bytes = b""
    msg_type: int = -1
    msg_final = None
    uin: int = -1
    sendtime: int = -1
    