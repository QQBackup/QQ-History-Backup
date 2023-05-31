import os
requirements = (
    ("ffmpeg 语音格式转换", ["av"]),
    ("pilk 语音解码", ["pilk"]),
    ("Android 导入", ["protobuf"]),
    ("Windows 导入", ["uttlv"]),
    ("Frida hook 数据库密钥", ["frida"]),
    ("HTML 导出", []),
    ("web 操作界面", []),
)
result = []
for name, libs in requirements:
    if not libs:
        continue
    # verify libs chars
    error = False
    for lib in libs:
        if [c for c in lib if not c.isalnum() and c not in "_-[]"]:
            result.append(f"[!] 安装 {name} ({libs}) 失败，库名不合法")
            error = True
            break
    if error:
        continue
    ret = os.system("pip install " + " ".join(libs))
    if ret != 0:
        result.append(f"[!] 安装 {name} ({libs}) 失败")
    else:
        result.append(f"[+] 安装 {name} ({libs}) 成功")
print("\n".join(result))
