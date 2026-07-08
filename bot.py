"""Discord 機器人主程式。

啟動流程：載入環境變數 → 建立 Bot → 載入 cogs → 同步斜線指令。
"""
import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("bot")

# message_content intent 是「被 @提及時用 AI 回覆」功能需要的，
# 記得去 Discord Developer Portal 開啟 MESSAGE CONTENT INTENT
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

COGS = ["cogs.fun", "cogs.chat"]


@bot.event
async def on_ready():
    log.info("已登入：%s (ID: %s)", bot.user, bot.user.id)
    # 同步斜線指令到 Discord（第一次啟動後，指令可能要幾分鐘才會出現）
    synced = await bot.tree.sync()
    log.info("已同步 %d 個斜線指令", len(synced))


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    # interaction token 在極少數網路延遲下會過期（Discord 3 秒回應限制），
    # 這種情況已經沒有互動可以回覆了，記錄下來就好，不用當成程式錯誤處理
    original = getattr(error, "original", error)
    if isinstance(original, discord.NotFound):
        log.warning("Interaction 已過期，忽略：%s", original)
        return
    log.exception("斜線指令發生未預期錯誤", exc_info=error)


async def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise SystemExit("找不到 DISCORD_TOKEN，請先複製 .env.example 為 .env 並填入你的 Bot Token")

    async with bot:
        for cog in COGS:
            await bot.load_extension(cog)
            log.info("已載入 %s", cog)
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
