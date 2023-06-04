from typing import Union
from app.Message.MessageHandler import MessageHandler
from app.i18n import t
from app.Chat import Friend, Group


@MessageHandler.register
class BaseMessage:
    support_msgtypes: list = []
    msgtype: str = ""  # 实际的消息类型，注意不能是 int
    description: str = "message.type.template"  # 消息类型描述
    is_file: bool = False  # 是否是文件类型的消息
    sender: Union[Friend, Group] = None  # 发送者
    time: int = None  # 发送时间
    content = None # 消息内容

    def to_file(self, path: str) -> None:
        raise NotImplementedError
        # 仅用于文件类型的消息

    def to_text(self) -> str:
        return t("message.type.middle_bracket").format(message_type=t(self.description))
        # 任意类型均可，必须返回单个可读取的字符串

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.msgtype} {self.to_text()}>"
