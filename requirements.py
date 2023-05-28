import os
requirements = (
    ("ffmpeg 语音格式转换", ["av"]),
    ("pilk 语音解码", ["pilk"]),
    ("Android 导入", ["protobuf"]),
    ("Windows 导入", ["uttlv"]),
    ("HTML 导出", []),
    ("web 操作界面", []),
)
result = []
for name, libs in requirements:
    if not libs:
        continue
    ret = os.system("pip install " + " ".join(libs))
    if ret != 0:
        result.append(f"[!] 安装 {name} ({libs}) 失败")
    else:
        result.append(f"[+] 安装 {name} ({libs}) 成功")
print("\n".join(result))
