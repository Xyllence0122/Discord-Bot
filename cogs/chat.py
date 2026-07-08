"""AI 聊天功能：@提及機器人 或用 /ask 跟 Gemini 對話，並附帶頻道對話記憶。

用 Gemini 是因為免費額度（不需要綁信用卡），對閒聊機器人這種用途很夠用。
"""
import asyncio
import logging
import os

import discord
from discord import app_commands
from discord.ext import commands
from google import genai

log = logging.getLogger("bot.chat")

MODEL = "gemini-2.5-flash"
SYSTEM_PROMPT = (
    "你是一個活潑友善的 Discord 機器人助手，使用繁體中文回覆。"
    "回答盡量簡潔，避免不必要的長篇大論，除非使用者要求詳細說明。"
)
DISCORD_MSG_LIMIT = 2000


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None
        # 每個頻道各自一個 chat session，物件本身會記住對話歷史
        self.chats: dict[int, "genai.chats.Chat"] = {}

    def _get_chat(self, channel_id: int):
        chat = self.chats.get(channel_id)
        if chat is None:
            chat = self.client.chats.create(
                model=MODEL,
                config={"system_instruction": SYSTEM_PROMPT},
            )
            self.chats[channel_id] = chat
        return chat

    async def _ask_gemini(self, channel_id: int, user_text: str) -> str:
        if self.client is None:
            return "⚠️ 尚未設定 GEMINI_API_KEY，AI 聊天功能無法使用。"

        chat = self._get_chat(channel_id)
        try:
            # google-genai 的 client 是同步的，丟到 thread 避免卡住 Discord 的事件迴圈
            response = await asyncio.to_thread(chat.send_message, user_text)
        except Exception:
            log.exception("呼叫 Gemini API 失敗")
            return "❌ 呼叫 AI 時發生錯誤，請稍後再試。"

        return response.text or "（沒有收到回覆內容）"

    @staticmethod
    def _strip_mention(content: str, bot_user: discord.ClientUser) -> str:
        return content.replace(f"<@{bot_user.id}>", "").replace(f"<@!{bot_user.id}>", "").strip()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or self.bot.user not in message.mentions:
            return

        user_text = self._strip_mention(message.content, self.bot.user)
        if not user_text:
            await message.reply("有什麼我可以幫忙的嗎？可以直接 @我 問問題，或用 `/ask`。")
            return

        async with message.channel.typing():
            reply = await self._ask_gemini(message.channel.id, user_text)
        await self._send_chunked(message.reply, reply)

    @app_commands.command(name="ask", description="問 AI 一個問題")
    @app_commands.describe(question="你想問的問題")
    async def ask(self, interaction: discord.Interaction, question: str):
        await interaction.response.defer()
        reply = await self._ask_gemini(interaction.channel_id, question)
        await self._send_chunked(interaction.followup.send, reply)

    @app_commands.command(name="reset_chat", description="清除這個頻道跟 AI 的對話記憶")
    async def reset_chat(self, interaction: discord.Interaction):
        self.chats.pop(interaction.channel_id, None)
        await interaction.response.send_message("🧹 對話記憶已清除。", ephemeral=True)

    @staticmethod
    async def _send_chunked(send_fn, text: str):
        for i in range(0, len(text), DISCORD_MSG_LIMIT):
            await send_fn(text[i : i + DISCORD_MSG_LIMIT])


async def setup(bot: commands.Bot):
    await bot.add_cog(Chat(bot))
