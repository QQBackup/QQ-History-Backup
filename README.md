
# QQ聊天记录导出

[Github下载链接](https://github.com/Young-Lord/QQ-History-Backup/releases) ，不可直接运行。

## 简介

作为国内最常用的聊天工具之一，QQ 为了用户留存度，默认聊天记录备份无法脱离 QQ 被独立打开。

目前版本往往需要自行编译，本方法在之前版本的基础上简化了操作，制作了GUI方便使用；并且不再需要提供密钥，自动填入备注/昵称，添加了QQ表情和图片的一并导出。

## 获取聊天记录文件夹方法

> 注：以下提到的“电脑”泛指一切可以运行此程序的环境，如安卓手机上的 Termux 也属于此列

如果手机已获得 root 权限，聊天记录可在以下路径找到。

```
data\data\com.tencent.mobileqq
```

我们需要的文件只有`databases/<QQ号>.db`，`databases/slowtable_<QQ号>.db`，`files/kc`，因此您可以将整个文件夹压缩后传输到电脑上，亦或将这三个文件单独放在同一个目录中传输。本程序会自动识别这两种不同的目录结构。

如果没有 root权限，可以通过手机自带的备份工具备份整个 QQ，拷贝备份文件到电脑，解压找到 `com.tencent.mobileqq`。

具体方法可以参见

> 怎样导出手机中的QQ聊天记录？ - 益新软件的回答 - 知乎
> <https://www.zhihu.com/question/28574047/answer/964813560>

如果同时需要在聊天记录中显示图片，拷贝手机中 `Android/data/com.tencent.mobileqq/Tencent/MobileQQ/chatpic/chatimg` 至 `GUI.exe` 同一文件夹中或者拷贝过来的`com.tencent.mobileqq`目录下。

## GUI使用方法

![GUI_image](./img/GUI.png)

- `com.tencent.mobileqq`：选择导出的相应文件夹，一般为`apps/com.tencent.mobileqq`
- 表情版本：默认为新版QQ表情。如果你的聊天记录来自很早以前（比如我），可以切换为旧版的表情
- 导出所有记录：若此项选择“是”，则`QQ号/群号：`与`私聊/群聊：`选项会被忽略。
- 合并图片：默认为否
  - 不启用合并图片好处在于：1. 使导出的 HTML 文件具有可读性；2. 减小 HTML 文件体积方便打开
  - 启用合并图片好处：拷贝时不需要和 `emoticon` 以及 `chatimg` 文件夹一起拷贝，更加方便

## 输出截图

![screenshot](./img/layout.png)
![screenshot](./img/images.png)

如果没有启用合并图片，拷贝生成的聊天记录时需要一起拷贝 `emoticon` 以及 `chatimg` 文件夹.

有 bug 的话提 issue，记得附上 log.txt 里的内容以及终端的报错内容。

## TODO

- [x] 支持群聊导出
- [x] 支持自动查找密钥
- [x] 使用好友/群聊昵称作为默认用户名
- [x] 自动合并 db 和 slow-table
- [x] 支持新 QQ emoji
- [x] 支持单一文件导出
- [ ] 支持 iOS 导出
- [ ] 支持视频导出
- [ ] 支持音频导出
- [ ] 使用脱敏文件作为 e2e 测试
- [ ] 添加 Makefile 自动化 build/test
- [ ] 支持缩略图
- [ ] 支持卡片分享

## FAQ

- **聊天记录中显示 `[图片]` 是因为什么？**

   解码出的图片路径在 `chatimg` 找不到相应文件。可能原因为在手机中没有加载过该文件，导致图片没有存在手机里。

## CHANGELOG

### v2

- 直接从 `files/kc` 提取明文的密钥，不用再手动输入或解密
- 支持群聊记录导出
- 支持 私聊/群聊 的 备注/昵称 自动填入
- 支持 slowtable 的直接整合
- 支持新版 QQ 表情

### v2.2

- 支持导出图片至聊天记录
- 支持合并图片至单一文件方便传输

### v2.3

- 支持读取不同的目录结构
- 支持单独导出一个私聊对话或群聊对话
- 部分修复解密函数存在的 bug
- 支持批量导出
- 修复导出的 HTML 中的字符转义

## 致谢

1. [roadwide/qqmessageoutput](https://github.com/roadwide/qqmessageoutput)
2. [WincerChan/export.py](https://gist.github.com/WincerChan/362331456a6e0417c5aa1cf3ff7be2b7)

3. [Yiyiyimu/QQ-History-Backup](https://github.com/Yiyiyimu/QQ-History-Backup)
