import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
from icon import ico, github_mark
import base64
import QQ_History
import os
import webbrowser
from time import sleep


def Enter():
    base_path, qq_self, qq = e1.get(), e2.get(), e3.get()
    group = 1 if e4.get() == '私聊' else 2
    emoji = 1 if e5.get() == '新' else 2
    dump_all = True if e8.get() == '是' else False
    with_img = True if e6.get() == '是' else False
    combine_img = True if e7.get() == '是' else False
    if (base_path == "" or qq_self == "") or (qq == "" and (not dump_all)):
        info.set("信息不完整！")
        return ()
    # info.set("开始导出……")
    # if dump_all:
    #     info.set("批量导出较慢，请耐心等待……")
    # 只要界面未更新 用户就看不到
    try:
        QQ_History.main(base_path, qq_self, qq, group,
                        emoji, with_img, combine_img, dump_all=dump_all)
        info.set("导出完成。")
    except Exception as e:
        info.set(repr(e))
    return ()


def SelectDBPath():
    dir = filedialog.askdirectory()
    base_path_get.set(dir)


def SelectImgPath():
    dir = filedialog.askdirectory()
    img_path_get.set(dir)


def url():
    webbrowser.open_new("https://github.com/Young-Lord/QQ_History_Backup")


root = tk.Tk()
base_path_get, img_path_get, key_get, info = tk.StringVar(
), tk.StringVar(), tk.StringVar(), tk.StringVar()

tmp = open("tmp.ico", "wb+")
tmp.write(base64.b64decode(ico))
tmp.close()
root.iconbitmap("tmp.ico")
os.remove("tmp.ico")

root.title("QQ聊天记录导出")

ttk.Label(root, text="*com.tencent.mobileqq：").grid(row=0, column=0, sticky="e")
e1 = ttk.Entry(root, textvariable=base_path_get)
e1.grid(row=0, column=1, columnspan=2, sticky="ew", pady=3)
ttk.Button(root, text="选择", command=SelectDBPath,
           width=5).grid(row=0, column=3)

ttk.Label(root, text="*自己QQ号：").grid(row=1, column=0, sticky="e")
e2 = ttk.Entry(root)
e2.grid(row=1, column=1, columnspan=3, sticky="ew", pady=3)

ttk.Label(root, text="导出所有记录：").grid(
    row=2, column=0, sticky="e")  # 每个row属性都得更改，什么离谱布局
e8 = ttk.Combobox(root)
e8['values'] = ('是', '否')
e8.current(1)
e8.grid(row=2, column=1, columnspan=3, sticky="ew", pady=3)

ttk.Label(root, text="QQ号/群号：").grid(row=3, column=0, sticky="e")
e3 = ttk.Entry(root)
e3.grid(row=3, column=1, columnspan=3, sticky="ew", pady=3)

ttk.Label(root, text="私聊/群聊：").grid(row=4, column=0, sticky="e")
e4 = ttk.Combobox(root)
e4['values'] = ('私聊', '群聊')
e4.current(0)
e4.grid(row=4, column=1, columnspan=3, sticky="ew", pady=3)

ttk.Label(root, text="表情版本：").grid(row=5, column=0, sticky="e")
e5 = ttk.Combobox(root)
e5['values'] = ('新', '旧')
e5.current(0)
e5.grid(row=5, column=1, columnspan=3, sticky="ew", pady=3)

ttk.Label(root, text="导出图片：").grid(row=6, column=0, sticky="e")
e6 = ttk.Combobox(root)
e6['values'] = ('是', '否')
e6.current(0)
e6.grid(row=6, column=1, columnspan=3, sticky="ew", pady=3)

ttk.Label(root, text="合并图片：").grid(row=7, column=0, sticky="e")
e7 = ttk.Combobox(root)
e7['values'] = ('是', '否')
e7.current(1)
e7.grid(row=7, column=1, columnspan=3, sticky="ew", pady=3)

root.grid_columnconfigure(2, weight=1)
info.set("开始")
ttk.Button(root, textvariable=info, command=Enter).grid(row=8, column=1)

tmp = open("tmp.png", "wb+")
tmp.write(base64.b64decode(github_mark))
tmp.close()
github = tk.PhotoImage(file='tmp.png')
os.remove("tmp.png")

button_img = tk.Button(root, image=github, text='b', command=url, bd=0)
button_img.grid(row=9, rowspan=7, column=0, sticky="ws")

root.mainloop()
