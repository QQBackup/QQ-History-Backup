# QQ聊天记录导出

## 声明

本项目仅供学习交流使用，严禁用于任何违反中国大陆法律法规、您所在地区法律法规、[QQ软件许可及服务协议](https://rule.tencent.com/rule/preview/46a15f24-e42c-4cb6-a308-2347139b1201)的行为，本人不承担任何相关行为导致的直接或间接责任。

本项目理论仅能将可以通过正常方法查看的聊天记录**导出**，而不能进行包括但不限于已删除聊天记录恢复在内的操作。

本项目不对生成内容的完整性、准确性作任何担保，因此生成的一切内容**没有法律效力**，您不应当将其用于学习与交流外的任何用途。

## 简介

作为国内最常用的聊天工具之一，QQ 为了用户留存度，默认聊天记录备份无法脱离 QQ 被独立打开。

目前版本往往需要通过命令行运行，本方法在之前版本的基础上简化了操作，制作了GUI方便使用；并且不再需要提供密钥，自动填入备注/昵称，添加了QQ表情、图片和语音的一并导出。

### 打包版本下载

本项目使用 GitHub Actions 构建了 PyInstaller 打包版，适用于 64 位 Windows 系统。你可以在以下两处下载：

- [GitHub Actions 页面](https://github.com/Young-Lord/QQ-History-Backup/actions)：需登录，文件自生成起90天后过期，保证基于最新代码

- [GitHub Releases 页面](https://github.com/Young-Lord/pyinstaller/releases/latest)：不需登录，文件不过期，但不一定基于最新代码

下载完成后，双击运行。

### 直接运行

1. 一切操作之前，你需要先安装 Python 3.x（建议使用可下载的最高版本，已知支持`3.12`），可参考[此文章（Windows）](https://zhuanlan.zhihu.com/p/458428159)。
2. 然后，在当前目录打开终端，Windows 用户若不懂可以看[这篇博文](https://blog.csdn.net/Lzy410992/article/details/105937780)
3. 输入以下命令永久加速相关依赖的下载（换源）：`pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple`
3. 安装依赖：`pip install -r requirements.txt`
4. 若是运行 GUI，就`python GUI.py`
5. 若是直接运行命令行版，就修改好`app/QQ_History.py`最下面的内容，并运行：`python main.py`

## 获取聊天记录文件夹方法

> 注：以下提到的“电脑”泛指一切可以运行此程序的环境，如安卓手机上的 Termux 也属于此列

> 注：以下内容假设您使用的是 QQ 而非 TIM，如果您在使用 TIM，请将`com.tencent.mobileqq`改为`com.tencent.tim`，将`MobileQQ`改为`Tim`

如果手机已获得 root 权限，聊天记录可在以下路径找到。

```
/data/data/com.tencent.mobileqq/
```

我们需要的文件只有`databases/<QQ号>.db`，`databases/slowtable_<QQ号>.db`，`files/kc`，因此您可以将整个文件夹压缩后传输到电脑上，亦或将这三个文件单独放在同一个目录中传输。本程序会自动识别这两种不同的目录结构。

如果没有 root 权限，可以通过手机自带的备份工具备份整个 QQ，拷贝备份文件到电脑，解压找到 `com.tencent.mobileqq`。

具体方法可以参见

> 怎样导出手机中的QQ聊天记录？ - 益新软件的回答 - 知乎
> <https://www.zhihu.com/question/28574047/answer/964813560>

关于苹果设备导出，参见[此讨论](https://github.com/Yiyiyimu/QQ-History-Backup/issues/42)；对于安卓系统导出内容的提取，请自行在互联网查询。

如果同时需要在聊天记录中显示图片，拷贝手机中 `/sdcard/Android/data/com.tencent.mobileqq/Tencent/MobileQQ/chatpic/chatimg` 至 `GUI.exe` 同一文件夹中或者拷贝过来的`com.tencent.mobileqq`目录下。

（QQ）如果同时需要在聊天记录中显示语音，拷贝手机中 `/sdcard/Android/data/com.tencent.mobileqq/Tencent/MobileQQ/<QQ号>/ptt` 至 `GUI.exe` 同一文件夹中或者拷贝过来的`com.tencent.mobileqq`目录下。

（TIM）如果同时需要在聊天记录中显示语音，拷贝手机中 `/sdcard/Android/data/com.tencent.tim/Tencent/Tim/ptt/<QQ号>` 至 `GUI.exe` 同一文件夹中或者拷贝过来的`com.tencent.mobileqq`目录下，并重命名为`ptt`。

## GUI使用方法

![GUI_image](./img/GUI.png)

- `com.tencent.mobileqq`：选择导出的相应文件夹，对于备份方式，一般为`apps/com.tencent.mobileqq`
- 表情版本：默认为新版QQ表情。如果你的聊天记录来自很早以前，可以切换为旧版的表情
- 导出所有记录：若此项选择“是”，则`QQ号/群号：`与`私聊/群聊：`选项会被忽略。
- 导出图片：若此项与前一项均选择“是”，必须把`chatimg`目录复制到生成的`output_xxx`目录下，图片才能正常显示
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
- [x] 支持音频导出
- [ ] 支持视频导出
- [ ] 支持合并转发消息导出
- [ ] 支持戳一戳导出
- [ ] 支持缩略图
- [ ] 支持卡片分享
- [ ] 重构代码
- [ ] 加入 i18n 与自定义翻译支持
- [ ] 支持使用[silk-v3-decoder](https://github.com/ZhangJun2017/QQChatHistoryExporter)转换音频文件
- [ ] 使用 Jinja2 生成 HTML 文件
- [ ] 允许插入自定义 CSS 与 自定义 JS
- [ ] 分析并试图优化解密相关函数
- [ ] 更新预览图
- [ ] 基于 GitHub Actions 以 PyInstaller 生成在 Windows 下的可执行文件



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

### v2.4

- 支持读取音频

## 致谢

1. [roadwide/qqmessageoutput](https://github.com/roadwide/qqmessageoutput)

2. [WincerChan/export.py](https://gist.github.com/WincerChan/362331456a6e0417c5aa1cf3ff7be2b7)

3. [Yiyiyimu/QQ-History-Backup](https://github.com/Yiyiyimu/QQ-History-Backup) （本仓库的来源，致敬！同时，源代码基于 MIT 协议使用。）

4. [ZhangJun2017/QQChatHistoryExporter](https://github.com/ZhangJun2017/QQChatHistoryExporter) （参考了 Protobuf 相关内容）

## 适配新类型笔记

1. 下载 [protoc](https://github.com/protocolbuffers/protobuf/releases) 这一可执行文件，设置可执行权限（仅 Linux 类系统）并移动到适当位置（位于 PATH 环境变量中的目录）

2. 编辑`proto/RichMsg.proto`，增加新类型（可以参照[此项目](https://github.com/ZhangJun2017/QQChatHistoryExporter/blob/f97eb64581229a30514d55aa0a8423b138b09437/src/RawMessage.java#L41)）

3. 切换到目录`proto`中，运行`compile`，在 Windows 下需先将其改名为`compile.bat`

4. 编辑`QQ_History.py`中的`decrypt`，加入`msgtype`对应判断与处理代码

5. **记得写文档**
