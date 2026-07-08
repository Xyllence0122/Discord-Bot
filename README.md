# Discord Bot

一個用 Python (discord.py) 寫的 Discord 機器人，功能包含：

- 基本指令：`/ping`、`/roll`（擲骰子）、`/coinflip`、`/8ball`
- 伺服器/使用者資訊：`/userinfo`、`/serverinfo`
- AI 聊天：`@機器人` 直接聊天，或用 `/ask` 問問題（透過 Claude API，含頻道對話記憶）、`/reset_chat` 清除記憶

## 1. 建立 Discord Bot

1. 前往 [Discord Developer Portal](https://discord.com/developers/applications) → **New Application**
2. 左側選 **Bot** → **Add Bot**
3. 在 Bot 頁面：
   - 點 **Reset Token** 取得 Token（等等要填進 `.env`）
   - 開啟 **MESSAGE CONTENT INTENT**（AI 聊天功能需要）
4. 左側選 **OAuth2 → URL Generator**：
   - Scopes 勾選 `bot` 和 `applications.commands`
   - Bot Permissions 至少勾選：Send Messages、Read Message History、Use Slash Commands、Embed Links
   - 複製產生的網址，打開它把機器人邀請進你的伺服器

## 2. 本機設定

```bash
git clone <你的repo網址>
cd discord-bot
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
copy .env.example .env       # Windows；macOS/Linux 用 cp
```

編輯 `.env`，填入：

- `DISCORD_TOKEN`：上面拿到的 Bot Token
- `ANTHROPIC_API_KEY`：[Anthropic Console](https://console.anthropic.com/) 申請的 API Key（不需要 AI 聊天功能可留空，其他指令仍可正常運作）

## 3. 執行

```bash
python bot.py
```

第一次啟動後，斜線指令可能需要幾分鐘才會在 Discord 上出現。

## 4. 放上 GitHub

```bash
git init
git add .
git commit -m "Initial commit: Discord bot with fun commands and AI chat"
git branch -M main
git remote add origin <你的repo網址>
git push -u origin main
```

`.env` 已經被 `.gitignore` 排除，不會被上傳——金鑰不會外洩。

## 5. 部署（讓機器人 24 小時在線）

本機關機機器人就會離線。免費/低成本的持續運行方案：

- [Railway](https://railway.app)：連接 GitHub repo，設定環境變數，自動部署
- [Render](https://render.com)：Background Worker 服務
- 自己的 VPS + `systemd` 或 `pm2` 常駐執行

## 專案結構

```
discord-bot/
├── bot.py              # 進入點：載入 cogs、連線 Discord
├── cogs/
│   ├── fun.py          # 基本指令與娛樂功能
│   └── chat.py         # AI 聊天（Claude API）
├── requirements.txt
├── .env.example
└── .gitignore
```

## 擴充功能

想加新指令，就在 `cogs/` 底下新增檔案（參考 `fun.py` 的寫法），然後在 `bot.py` 的 `COGS` 列表加上模組名稱。
