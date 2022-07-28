import hashlib
import sqlite3
import time
import os
import traceback
import json
import base64
from proto.RichMsg_pb2 import PicRec
from proto.RichMsg_pb2 import Elem
from proto.RichMsg_pb2 import Msg
from html import escape

_crc64_init = False
_crc64_table = [0] * 256


def crc64(s):
    global _crc64_init
    if not _crc64_init:
        for i in range(256):
            bf = i
            for j in range(8):
                if bf & 1 != 0:
                    bf = bf >> 1 ^ -7661587058870466123
                else:
                    bf >>= 1
            _crc64_table[i] = bf
        _crc64_init = True
    v = -1
    for i in range(len(s)):
        v = _crc64_table[(ord(s[i]) ^ v) & 255] ^ v >> 8
    return v


def isEmpty(s):
    if s is None:
        return True
    if type(s) == int and s == 0:
        return True
    if type(s) == str and s == '':
        return True
    return False


class QQoutput():
    def __init__(self, base_path: str, qq_self: str, emoji: int = 1, with_img: bool = True, combine_img: bool = False):
        # 真正用到的文件只有[f"{QQ}.db", f"slowtable_{QQ}.db", "kc"]，这里我直接合并到一个层级下了
        self.base_path = base_path
        if type(qq_self) == int:
            qq_self = str(qq_self)
        assert(type(qq_self) == str)
        self.qq_self: str = qq_self  # 自己的QQ号
        self.uin_to_username = {}
        self.troopuin_to_troopname = {}
        self.troopuin_to_troopmembers = {}
        self.init_paths()
        self.init_key()  # 解密用的密钥
        self.c1 = sqlite3.connect(self.db_main_path).cursor()
        self.c2 = sqlite3.connect(self.db_slow_path).cursor()
        self.init_friend_list()
        self.init_troop_list()
#        self.qq: str = qq # 导出对象的QQ号
#        self.mode = mode # 1为私聊，2为群聊
        assert(emoji in (1, 2))
        self.emoji = emoji  # 1为新表情，2为旧表情
        assert(type(with_img) == bool)
        self.with_img = with_img  # True为生成图片，False为不生成图片
        assert(type(combine_img) == bool)
        self.combine_img = combine_img  # True为将图片嵌入HTML文件中，False为在HTML中存储图片的相对路径

        # self.num_to_name = {}
        # 双重映射，即self.troop_members_name[群号][发言人QQ号]
        self.troop_members_name = {}
        self.emoji_map = self.map_new_emoji()

    @staticmethod
    def getDisplayName(friend: list) -> str:
        if isEmpty(friend[1]):
            ans = friend[2]
        else:
            ans = friend[1]
        return ans

    @staticmethod
    def getSafePath(ans: str) -> str:
        ban_words = "\\  /  :  *  ?  \"  '  <  >  |  $  \r  \n".replace(
            ' ', '')
        ban_strips = "#/~"
        while True:
            ans_bak = ans
            for i in ban_words:
                ans = ans.replace(i, "")
            for i in ban_strips:
                ans = ans.strip(i)
            if ans == ans_bak:  # 多次匹配
                break
        return ans

    def mydecrypt(self, data):
        # 综合一下
        s = self.fix(data, 1)
        if s != "":
            return s
        return self.decrypt(data)

    def fix(self, data, mode):
        # msgdata mode=0
        # other mode=1
        # https://github.com/roadwide/qqmessageoutput/blob/master/q.py
        # decrypt处理Emoji时会出问题，而这个不会
        if (mode == 0):
            rowbyte = []
            # 这么做是为了解决汉字的utf-8是三字节
            for i in range(0, len(data)):
                rowbyte.append(data[i] ^ ord(self.key[i % len(self.key)]))
            rowbyte = bytes(rowbyte)
            try:
                msg = rowbyte.decode(encoding='utf-8')
            except:
                msg = ""
            return msg
        elif (mode == 1):
            str = ''
            try:
                j = 0
                for i in range(0, len(data)):
                    # 获取unicode码
                    unicode = ord(data[i])
                    # 如果大于ffff 处理emoji
                    if (unicode > 0xffff):
                        # 分为2个10位二进制与两个密码进行异或
                        code = unicode ^ (
                            (ord(self.key[i+j % len(self.key)]) << 10) + ord(self.key[i+j+1 % len(self.key)]))
                        str += chr(code)
                        j = j + 1
                    else:
                        str += chr(ord(data[i]) ^
                                   ord(self.key[i+j % len(self.key)]))
            except:
                str = ""
            return str

    def decrypt(self, data, msg_type=-1000):
        # fix处理**一些东西**会出问题，这个不会
        msg = b''
        if type(data) == bytes:
            msg = b''
            for i in range(0, len(data)):
                msg += bytes([data[i] ^ ord(self.key[i % len(self.key)])])
        elif type(data) == str:
            msg = ''
            for i in range(0, len(data)):
                msg += chr(ord(data[i]) ^ ord(self.key[i % len(self.key)]))
            return msg

        if msg_type == -1000 or msg_type == -1049 or msg_type == -1051:
            try:
                return escape(msg.decode('utf-8'))
            except:
                # print(msg)
                pass
                return '[decode error]'

        if not self.with_img:
            return None
        elif msg_type == -2000:
            return self.decode_pic(msg)
        elif msg_type == -1035:
            return self.decode_mix_msg(msg)
        elif msg_type == -5008:
            return self.decode_share_url(msg)
        elif msg_type == -5012 or msg_type == -5018:
            return '[戳一戳]'
        # for debug
        # return '[unknown msg_type {}]'.format(msg_type)
        return None

    def add_emoji(self, msg):
        pos = msg.find('\x14')
        while pos != -1:
            lastpos = pos
            num = ord(msg[pos + 1])
            if str(num) in self.emoji_map:
                index = self.emoji_map[str(num)]

                if self.emoji == 1:
                    filename = "new/s" + index + ".png"
                else:
                    filename = "old/" + index + ".gif"

                emoticon_path = os.path.join('emoticon', filename)
                if self.combine_img:
                    emoticon_path = self.get_base64_from_pic(emoticon_path)

                msg = msg.replace(
                    msg[pos:pos + 2], '<img src="{}" alt="{}" />'.format(emoticon_path, index))
            else:
                msg = msg.replace(msg[pos:pos + 2],
                                  '[emoji:{}]'.format(str(num)))
            pos = msg.find('\x14')
            if pos == lastpos:
                break
        return msg

    def message(self, qq: str, mode: int):
        # mode=1 friend
        # mode=2 troop
        num = qq.encode("utf-8")
        md5num = hashlib.md5(num).hexdigest().upper()
        if mode == 1:
            cmd = "select msgData,senderuin,time,msgtype from mr_friend_{}_New order by time".format(
                md5num)
#            self.get_friends()
        else:
            cmd = "select msgData,senderuin,time,msgtype from mr_troop_{}_New order by time".format(
                md5num)
            # print('Groups {} -> {}'.format(num, md5num))
            self.get_troop_members(qq)

        cursor = self.fill_cursor(cmd)
        allmsg = []
        for row in cursor:
            msgdata: bytes = row[0]
            if not msgdata:
                continue
            uin = row[1]
            ltime = time.localtime(row[2])
            sendtime = time.strftime("%Y-%m-%d %H:%M:%S", ltime)
            msg_type = row[3]
            msg_final = self.decrypt(msgdata, msg_type)
            if msg_final is None:
                continue

            allmsg.append(
                [sendtime, msg_type, self.decrypt(uin), msg_final])
        return allmsg

    def get_friends(self):
        raise NotImplementedError

    def get_troop_members(self, qq: str):
        self.troopuin_to_troopmembers[qq] = {}
        cmd = "SELECT troopuin, memberuin, autoremark, troopnick, friendnick, recommendRemark, mUniqueTitle FROM TroopMemberInfo"
        cursor = self.fill_cursor(cmd)
        for row in cursor:
            if self.fix(row[0], 1) != qq:
                continue
            num = self.fix(row[1], 1)
            names = [self.fix(i, 1) for i in row[2:6]]
            # 2是你给好友的备注，3是好友的群昵称，4是好友名字，5是好友的群昵称，mUniqueTitle是群头衔
            # xxx 我不知道这个顺序怎么搞的 一部分是猜
            try:
                final_name = [i for i in names[1:] if not isEmpty(i)][0]
            except IndexError:
                try:
                    final_name = names[0]
                except IndexError:
                    print(f"{qq}群中{num}好友无法匹配名字。names={names}")
                    print("开Issue！")
            if num in self.uin_to_username:  # 是你对话过的人
                if not isEmpty(names[0]):
                    final_name = names[0]
                else:
                    #                    print(names)
                    #                    print("↑你这个好友怎么没有备注的？开Issue！")
                    pass
            self.troopuin_to_troopmembers[qq][num] = final_name
#            print([self.fix(i, 1) for i in row[2:6]])
            if not isEmpty(row[6]):  # 添加头衔
                self.troopuin_to_troopmembers[qq][num] = f"【{row[6]}】" + \
                    self.troopuin_to_troopmembers[qq][num]

    def _fill_cursors(self, cmd):
        cursors = []
        # slowtable might not contain related message, so just skip it
        try:
            cursors.append(self.c2.execute(cmd))
        except:
            pass
        cursors.append(self.c1.execute(cmd))
        return cursors

    def fill_cursor(self, cmd):
        cursors = self._fill_cursors(cmd)
        for cs in cursors:
            for row in cs:
                yield row

    def output(self, qq: str, mode: int, output_path: str = "."):
        if type(qq) == int:
            qq = str(qq)
        assert(type(qq) == str)
        assert(mode in (1, 2))
        name1 = "我"
        if mode == 1:
            filebasename = self.getSafePath(self.uin_to_username[qq])
        else:
            filebasename = self.getSafePath(self.troopuin_to_troopname[qq])
        file = f"{filebasename}-{qq}.html"
        file = os.path.join(output_path, file)
        allmsg = self.message(qq, mode)
        if len(allmsg) == 0:
            print(f"{qq}_{mode}没有聊天记录，跳过。")
            return
        f2 = open(file, "w", encoding="utf-8")
        f2.write(
            "<head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" /></head>"
        )
        f2.write("<div style='white-space: pre-line'>")
        if mode == 1:
            table = self.uin_to_username
        else:
            table = self.troopuin_to_troopmembers[qq]
        for ts, _, uid, msg in allmsg:
            if not msg:
                continue
            if uid == str(self.qq_self):
                f2.write("<p align='right'>")
                f2.write("<font color=\"green\">")
                f2.write(ts)
                f2.write("</font>-----<font color=\"blue\"><b>")
                f2.write(name1)
                f2.write("</font></b></br>")
            else:
                f2.write("<p align='left'>")
                f2.write("<font color=\"blue\"><b>")
                f2.write(escape("{}({})".format(
                    table.get(uid, "？？？未知？？？"), uid)))
                f2.write("</b></font>-----<font color=\"green\">")
                f2.write(ts)
                f2.write("</font></br>")
            f2.write(self.add_emoji(msg))
            f2.write("</br></br>")
            f2.write("</p>")
        f2.write("</div>")
        f2.close()
        print("导出已完成。文件目录：" + file)

    def init_key(self):
        kc_file = open(self.kc_path, "r")
        self.key = kc_file.read().strip('\r \n')
        kc_file.close()

    def init_paths(self):
        join = os.path.join
        mainb = self.qq_self + ".db"
        slowb = "slowtable_" + self.qq_self + ".db"
        db_main_paths = [mainb, join("databases", mainb), join("db", mainb)]
        db_slow_paths = [slowb, join("databases", slowb), join("db", slowb)]
        kc_paths = ["kc", join("files", "kc"), join("f", "kc")]
        self.kc_path = self.db_main_path = self.db_slow_path = None
        for i in db_main_paths:
            current_file = join(self.base_path, i)
            if os.path.isfile(current_file):
                self.db_main_path = current_file
        for i in db_slow_paths:
            current_file = join(self.base_path, i)
            if os.path.isfile(current_file):
                self.db_slow_path = current_file
        for i in kc_paths:
            current_file = join(self.base_path, i)
            if os.path.isfile(current_file):
                self.kc_path = current_file
        if self.kc_path is None or self.db_main_path is None or self.db_slow_path is None:
            raise FileNotFoundError(
                f"无法找到目标文件！\n路径：{self.base_path}\n当前匹配列表：{[self.kc_path, self.db_main_path, self.db_slow_path]}")

    def init_friend_list(self):
        self.FriendsData = []
        # uin-QQ号，remark-备注，name-昵称
        execute = "select uin,remark,name from Friends"
        cursor = self.fill_cursor(execute)
        for i in cursor:
            uin, remark, name = i[0], i[1], i[2]
            decode_uin = self.mydecrypt(uin)
            decode_remark = self.mydecrypt(remark)
            decode_name = self.mydecrypt(name)
            friend = [decode_uin, decode_remark, decode_name]
            self.FriendsData.append(friend)
            self.uin_to_username[decode_uin] = self.getDisplayName(friend)

    def init_troop_list(self):
        self.TroopsData = []
        # troopuin-群号，troopRemark-群备注，troopname-群名
        execute = "select troopuin,troopRemark,troopname from TroopInfoV2"
        cursor = self.fill_cursor(execute)
        for i in cursor:
            uin, remark, name = i[0], i[1], i[2]
#            print([self.fix(ii,1) for ii in i])
            decode_uin = self.mydecrypt(uin)
            decode_remark = self.mydecrypt(remark)
            decode_name = self.mydecrypt(name)
            troop = [decode_uin, decode_remark, decode_name]
            self.TroopsData.append(troop)
#            print(troop)
            self.troopuin_to_troopname[decode_uin] = self.getDisplayName(troop)

    def map_new_emoji(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), './emoticon/face_config.json'), encoding='utf-8') as f:
            # 这个地方可能会在打包的时候出问题
            emojis = json.load(f)
        new_emoji_map = {}

        for e in emojis['sysface']:
            if self.emoji == 1:
                new_emoji_map[e["AQLid"]] = e["QSid"]
            else:
                if len(e["EMCode"]) == 3:
                    new_emoji_map[e["AQLid"]] = str(int(e["EMCode"]) - 100)
        return new_emoji_map

    def get_base64_from_pic(self, path):
        with open(path, "rb") as image_file:
            return (b'data:image/png;base64,' + base64.b64encode(image_file.read())).decode("utf-8")

    def decode_pic(self, data):
        try:
            doc = PicRec()
            doc.ParseFromString(data)
            url = 'chatimg:' + doc.md5
            filename = hex(crc64(url))
            filename = 'Cache_' + filename.replace('0x', '')
            chatimg_basepath = os.path.join(self.base_path, "chatimg")
            if not os.path.isdir(chatimg_basepath):
                chatimg_basepath = "chatimg"
            rel_path = os.path.join(chatimg_basepath, filename[-3:], filename)
            if os.path.exists(rel_path):
                print(rel_path)
                w = 'auto' if doc.uint32_thumb_width == 0 else str(
                    doc.uint32_thumb_width)
                h = 'auto' if doc.uint32_thumb_height == 0 else str(
                    doc.uint32_thumb_height)
                if self.combine_img:
                    rel_path = self.get_base64_from_pic(rel_path)
                return '<img src="{}" width="{}" height="{}" />'.format(os.path.join("chatimg", filename[-3:], filename), w, h)
                # 最后这里必须用相对路径
        except Exception as e:
            pass
        return '[图片]'

    def decode_mix_msg(self, data):
        try:
            doc = Msg()
            doc.ParseFromString(data)
            message = ''
            for elem in doc.elems:
                if elem.picMsg:
                    message += self.decode_pic(elem.picMsg)
                else:
                    message += escape(elem.textMsg.decode('utf-8'))
            return message
        except:
            pass
        return '[混合消息]'

    def decode_share_url(self, msg):
        # TODO
        return '[分享卡片]'


def main(base_path, qq_self, qq, mode, emoji, with_img, combine_img, dump_all):
    try:
        f = open('log.txt', 'w', encoding="utf-8")
    except:
        class ff:
            def write(): pass
            def close(): pass
        f = ff()
    global print
    print_bak = print

    def print(*arg, **kwarg):
        print_bak(*arg, **kwarg)
        f.write("[PRINT]: "+' '.join(arg)+"\n")
    try:
        q = QQoutput(base_path, str(qq_self), emoji, with_img, combine_img)
        if dump_all:
            print("正在批量导出……")
            dest = "output_" + \
                time.strftime("%Y%m%d-%H%M%S", time.localtime(time.time()))
            try:
                os.mkdir(dest)
            except:
                raise ValueError("目录创建失败，退出。")
            for i in q.FriendsData:
                try:
                    q.output(i[0], 1, dest)
                except Exception as e:
                    f.write(repr(e))
                    f.write(traceback.format_exc())
            for i in q.TroopsData:
                try:
                    q.output(i[0], 2, dest)
                except Exception as e:
                    f.write(repr(e))
                    f.write(traceback.format_exc())
            print("")
            print("="*30)
            print("所有记录导出完成。")
            print("="*30)
        else:
            q.output(qq, mode)
    except Exception as e:
        f.write(repr(e))
        f.write(traceback.format_exc())

        print(traceback.format_exc())
        if repr(e).split(":")[0] == "OperationalError('no such table":
            raise ValueError("信息填入错误")
        else:
            raise BaseException("Error! See log.txt")


def run_directly():
    base_path = r"修改这里！"  # com.tencent.mobileqq 路径
    qq_self = "修改这里！"  # 自己的QQ号
    batch = True  # 是否导出所有记录
    q = QQoutput(base_path, str(qq_self))
    f = open('log.txt', 'w', encoding="utf-8")
    if batch:
        print("正在批量导出……")
        dest = "output_" + \
            time.strftime("%Y%m%d-%H%M%S", time.localtime(time.time()))+"_"
        try:
            os.mkdir(dest)
        except:
            raise ValueError("目录创建失败，退出。")
        for i in q.FriendsData:
            try:
                q.output(i[0], 1, dest)
            except Exception as e:
                f.write(repr(e))
                f.write(traceback.format_exc())
        for i in q.TroopsData:
            try:
                q.output(i[0], 2, dest)
            except Exception as e:
                f.write(repr(e))
                f.write(traceback.format_exc())
        print("")
        print("="*30)
        print("所有记录导出完成。")
        print("="*30)

    else:
        qq = "修改这里！"
        mode = 1  # 修改这里！私聊为1，群聊为2
        q.output(qq, mode)
    f.close()


if __name__ == '__main__':
    run_directly()
