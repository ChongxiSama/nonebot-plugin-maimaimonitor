# NoneBot Plugin: Maimai Monitor

一个为 [NoneBot2](https://nonebot.dev/) 框架设计的插件，用于通过聊天指令上报 maimai 服务器状态

## 功能

- [x] 状态上报: 通过简单的聊天指令（如 `/report 断网`）上报服务器状态
- [x] 数据聚合: 自动缓存用户上报数据，每 30 秒打包发送至后端 API
- [x] 自定义命令别名: 允许用户在配置中定义简洁的命令别名 映射到复杂的报告指令
- [ ] 直接抓取页面并渲染

## 安装

你可以通过 NoneBot 的脚手架工具 `nb-cli` 安装：

```bash
nb plugin install nonebot-plugin-maimaimonitor
```

或者通过 `pip` 安装：

```bash
pip install nonebot-plugin-maimaimonitor
```

## 配置

插件的配置项通过 NoneBot 的统一配置方式进行管理，你需要在你的 NoneBot 项目根目录下的 `.env` 文件中设置

### 获取凭证

为了向后端 API 发送数据，你需要一个 `ClientID` 和 `PRIVATE_KEY`。请联系 email:qwq@chongxi.us 获取。`ClientID`由您提供，建议为数字

**请妥善保管你的 `PRIVATE_KEY`，不要泄露给任何人。**

### 环境变量

| 环境变量              | 类型   | 默认值                  | 说明                                   |
| :-------------------- | :----- | :---------------------- | :------------------------------------- |
| `MAIMAI_BOT_CLIENT_ID` | `str`  | 无                      | ClientID (必要)             |
| `MAIMAI_BOT_PRIVATE_KEY` | `str`  | 无                      | 私钥 (必要)                  |
| `MAIMAI_BOT_DISPLAY_NAME` | `str`  | `qwq`                   | 您bot的名称           |
| `MAIMAI_WORKER_URL`   | `str`  | `https://maiapi.chongxi.us` | 上报数据后端的 API 地址  |
| `COMMAND_ALIASES`     | `Dict[str, str]` | `{}` | 自定义命令别名，用于将简洁命令映射到报告指令 |

### `.env` 配置文件示例

```dotenv
# .env 文件 (位于你的 NoneBot 项目根目录)

# --- NoneBot Plugin Maimai Monitor 插件核心配置 ---
MAIMAI_BOT_CLIENT_ID="YOUR_BOT_CLIENT_ID"
MAIMAI_BOT_PRIVATE_KEY="YOUR_BOT_PRIVATE_KEY"
MAIMAI_BOT_DISPLAY_NAME="qwqbot"
MAIMAI_WORKER_URL="https://maiapi.chongxi.us"

# --- 自定义命令别名配置 (使用单行 JSON 字符串) ---
# 左边是用户输入的新命令，右边是它映射的内部报告指令参数字符串。
# 右边的字符串会被插件解析，并作为 /report 命令的参数部分。
COMMAND_ALIASES="{ \
    \"ctk\": \"被发票\", \
    \"清票\": \"被发票\", \
    \"服务器炸了\": \"断网\", \
    \"打不开公众号\": \"NET打不开\", \
    \"变游客了\": \"无法登录\", \
    \"黑屋了\": \"小黑屋\", \
    \"被发舞神了\": \"其他扫号行为\", \
    \"罚站300秒\": \"罚站 300\", \
    \"罚站一小时\": \"罚站 3600\", \
    \"帮助\": \"help\" \
}"
```

## 使用

在你的 NoneBot 项目 `bot.py` 文件中加载插件：

```python
# bot.py
import nonebot

# ... 其他初始化代码 ...

nonebot.load_plugin("nonebot_plugin_maimaimonitor")

# ... nonebot.run() ...
```

插件加载成功后，你可以在与机器人聊天的任何地方发送以下指令：

*   `/report help` 或 `/上报 帮助`: 查看全部可用的上报类型和帮助信息
*   **使用自定义命令别名**: 例如，如果你在 `COMMAND_ALIASES` 中配置了 `"ctk": "被发票"`，那么直接发送 `ctk` 即可触发 `/report 被发票` 的功能

**部分命令示例**:
*   `/report 断网` 或 配置的别名（如 `炸了`）: 上报一次机台网络断开事件
*   `/report 罚站 [秒数]` 或 配置的别名（如 `罚站五分钟`）: 上报玩家罚站时长，例如 `/report 罚站 300` 表示罚站 5 分钟

## 主动 Dashboard 渲染

未来将会支持直接将前端渲染为SVG并转化为图片，当前仍需要截取 `https://mai.chongxi.us/?share=true&dark=auto`

`share` 为 bot 特殊优化的页面，`dark` 用于切换深色模式，`auto` 会自动根据时间切换。

## 贡献

欢迎提交 PR。
