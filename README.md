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

## 5. 部署到 Render（讓機器人 24 小時在線）

本機關機機器人就會離線，所以要部署到雲端。這個專案已經附上 `render.yaml`，用 Render 的 Blueprint 功能可以一次設定好：

1. 前往 [Render Dashboard](https://dashboard.render.com/) → 用 GitHub 帳號登入
2. **New** → **Blueprint**
3. 選擇這個 GitHub repo（`Discord-Bot`），Render 會自動讀取 `render.yaml`
4. 部署設定頁會要求輸入兩個環境變數（因為標記了 `sync: false`，金鑰不會存進 repo）：
   - `DISCORD_TOKEN`
   - `ANTHROPIC_API_KEY`
5. 按下 **Apply** / **Deploy**，Render 會自動 `pip install -r requirements.txt` 然後執行 `python bot.py`
6. 部署完成後到 **Logs** 分頁確認看到「已登入」字樣，代表機器人成功上線

之後每次 `git push` 到 `main`，Render 會自動重新部署最新版本。

> 記得部署後把本機執行中的 `python bot.py` 關掉，同一個 Token 兩邊同時跑，Discord 上每個指令都會回覆兩次。

其他選項：[Railway](https://railway.app)（連接 GitHub repo 也很直覺）、自己的 VPS + `systemd`/`pm2` 常駐執行。

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
