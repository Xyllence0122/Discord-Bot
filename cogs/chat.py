"""AI 聊天功能：@提及機器人 或用 /ask 跟 Claude 對話，並附帶頻道對話記憶。"""
import logging
import os

import discord
from anthropic import AsyncAnthropic
from discord import app_commands
from discord.ext import commands

log = logging.getLogger("bot.chat")

MODEL = "claude-opus-4-8"
SYSTEM_PROMPT = (
    "你是一個活潑友善的 Discord 機器人助手，使用繁體中文回覆。"
    "回答盡量簡潔，避免不必要的長篇大論，除非使用者要求詳細說明。"
)
MAX_HISTORY_TURNS = 10  # 每個頻道保留的對話輪數上限
DISCORD_MSG_LIMIT = 2000


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = AsyncAnthropic(api_key=api_key) if api_key else None
        # 每個頻道各自的對話歷史：{channel_id: [{"role": ..., "content": ...}, ...]}
        self.history: dict[int, list[dict]] = {}

    def _get_history(self, channel_id: int) -> list[dict]:
        return self.history.setdefault(channel_id, [])

    def _push_history(self, channel_id: int, role: str, content: str):
        history = self._get_history(channel_id)
        history.append({"role": role, "content": content})
        # 只保留最近 N 輪（一輪 = user + assistant，所以乘以 2）
        overflow = len(history) - MAX_HISTORY_TURNS * 2
        if overflow > 0:
            del history[:overflow]

    async def _ask_claude(self, channel_id: int, user_text: str) -> str:
        if self.client is None:
            return "⚠️ 尚未設定 ANTHROPIC_API_KEY，AI 聊天功能無法使用。"

        self._push_history(channel_id, "user", user_text)
        try:
            response = await self.client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=self._get_history(channel_id),
            )
        except Exception:
            log.exception("呼叫 Claude API 失敗")
            return "❌ 呼叫 AI 時發生錯誤，請稍後再試。"

        if response.stop_reason == "refusal":
            return "抱歉，這個請求我無法回答。"

        text = next((b.text for b in response.content if b.type == "text"), "")
        self._push_history(channel_id, "assistant", text)
        return text or "（沒有收到回覆內容）"

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
            reply = await self._ask_claude(message.channel.id, user_text)
        await self._send_chunked(message.reply, reply)

    @app_commands.command(name="ask", description="問 AI 一個問題")
    @app_commands.describe(question="你想問的問題")
    async def ask(self, interaction: discord.Interaction, question: str):
        await interaction.response.defer()
        reply = await self._ask_claude(interaction.channel_id, question)
        await self._send_chunked(interaction.followup.send, reply)

    @app_commands.command(name="reset_chat", description="清除這個頻道跟 AI 的對話記憶")
    async def reset_chat(self, interaction: discord.Interaction):
        self.history.pop(interaction.channel_id, None)
        await interaction.response.send_message("🧹 對話記憶已清除。", ephemeral=True)

    @staticmethod
    async def _send_chunked(send_fn, text: str):
        for i in range(0, len(text), DISCORD_MSG_LIMIT):
            await send_fn(text[i : i + DISCORD_MSG_LIMIT])


async def setup(bot: commands.Bot):
    await bot.add_cog(Chat(bot))
