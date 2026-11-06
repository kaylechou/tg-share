# tg-share — TG 转发站

所有要发到 Telegram 的文件都放这里，推送即自动同步到 TG。

## 怎么用

- **自动同步**：把文件推送到 `main` 分支，就会发到 TG（`.github/` 与 `README.md` 除外）。
- **手动发送**：Actions → Forward files to Telegram → Run workflow，填 `file_path`（仓库路径）和 `message`（先发的文字，可空）。

## 发送规则

- 图片 ≤10MB 发照片，mp4/mov 发视频流，gif 发动画，mp3/m4a 发音频，其余发文件。
- 单文件超过 50MB（Bot API 上限）不发文件，只发 raw 下载链接。
- 私聊限速约 1 条/秒，多文件依次发送。

## 需要的仓库 secret

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
