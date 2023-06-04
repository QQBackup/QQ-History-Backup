from typing import Union
class AndroidQqDecrypt(object):
    def __init__(self, key):
        self.key = key

    def decrypt(self, data: bytes) -> Union[str,None]:
        if data is None:
            return None
        try:
            s = self._fix(data, 1)
            if s is not None:
                return s
        except:
            pass
        return self._decrypt(data)

    def _decrypt(self, data):
        # fix处理**一些东西**会出问题，这个不会
        msg = b""
        if type(data) == bytes:
            msg = b""
            for i in range(0, len(data)):
                msg += bytes([data[i] ^ ord(self.key[i % len(self.key)])])
            return msg
        elif type(data) == str:
            msg = ""
            for i in range(0, len(data)):
                msg += chr(ord(data[i]) ^ ord(self.key[i % len(self.key)]))
            return msg
        else:
            raise ValueError("data must be bytes or str")


    def _fix(self, data: bytes, mode: int):
        # msgdata mode=0
        # other mode=1
        # https://github.com/roadwide/qqmessageoutput/blob/master/q.py
        # decrypt处理Emoji时会出问题，而这个不会
        assert isinstance(data, str), data
        if mode == 0:
            rowbyte = []
            # 这么做是为了解决汉字的utf-8是三字节
            for i in range(0, len(data)):
                rowbyte.append(data[i] ^ ord(self.key[i % len(self.key)]))
            rowbyte = bytes(rowbyte)
            try:
                msg = rowbyte.decode(encoding="utf-8")
            except:
                return None
            return msg
        elif mode == 1:
            rowstr = ""
            j = 0
            for i in range(0, len(data)):
                # 获取unicode码
                unicode = ord(data[i])
                # 如果大于ffff 处理emoji
                if unicode > 0xFFFF:
                    # 分为2个10位二进制与两个密码进行异或
                    code = unicode ^ (
                        (ord(self.key[i + j % len(self.key)]) << 10)
                        + ord(self.key[i + j + 1 % len(self.key)])
                    )
                    rowstr += chr(code)
                    j = j + 1
                else:
                    try:
                        rowstr += chr(ord(data[i]) ^ ord(self.key[i + j % len(self.key)]))
                    except IndexError:
                        return None
            return rowstr
        else:
            raise ValueError("mode must be 0 or 1")
