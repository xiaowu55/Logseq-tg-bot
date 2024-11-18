# Logseq Telegram Bot

一个用于将 Telegram 消息同步到 Logseq 的机器人。

## 功能

- 将消息自动同步到 Logseq 日志
- 支持 TODO 列表（发送 "TODO + 文本" 自动转换）
- 支持链接收藏（自动添加时间戳和标签）
- 支持图片和文件上传（自动保存到 assets 目录）
- 支持自定义文件路径（使用 >>path/to/file: content 格式）
- 自动生成最近7天的日历导航
- 支持 Hypothesis 注释同步（可选）
- 支持 Age 加密（可选）

## 安装

1. 克隆仓库
```bash
git clone https://github.com/your-username/logseq-telegram.git
cd logseq-telegram
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置
- 复制 `config/config.sample.ini` 为 `config/config.ini`
- 填写必要的配置信息：
  - Telegram Bot Token（从 @BotFather 获取）
  - 授权的 Telegram 用户 ID
  - GitHub 个人访问令牌
  - GitHub 仓库信息

## 使用

1. 启动机器人
```bash
python -m telegram_logseq.main
```

2. 功能说明
- 直接发送消息：添加到当天的日志
- TODO 格式：`TODO 买牛奶` -> `- LATER 买牛奶`
- 发送链接：自动添加时间戳和书签标签
- 发送图片：自动保存到 assets 目录
- 自定义路径：`>>pages/projects/todo.md: 完成文档` -> 添加到指定文件

## 配置说明

### Bot
- `BotToken`: Telegram Bot Token
- `BotName`: 机器人名称
- `AuthorizedIds`: 授权的用户 ID（逗号分隔）

### GitHub
- `Token`: GitHub 个人访问令牌
- `Branch`: 仓库分支名
- `User`: GitHub 用户名
- `Repo`: Logseq 仓库名
- `Author`: Git 提交作者
- `Email`: Git 提交邮箱
- `UpdateFrequency`: 更新频率（分钟）

### Journal
- `Hour24`: 是否使用24小时制
- `DefaultIndentLevel`: 默认缩进级别
- `TimestampEntries`: 是否添加时间戳
- `JournalsPrefix`: 日志文件前缀
- `JournalsFilesFormat`: 日志文件日期格式
- `JournalsFilesExtension`: 日志文件扩展名
- `BookmarkTag`: 书签标签

### AgeEncryption（可选）
- `Encrypted`: 是否启用加密
- `PublicKey`: Age 公钥
- `PrivateKey`: Age 私钥

### Hypothesis（可选）
- `Token`: Hypothesis API Token

## 许可证

MIT License