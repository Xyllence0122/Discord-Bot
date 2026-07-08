"""基本指令 + 娛樂功能：ping、擲骰子、猜拳、8號球、伺服器/使用者資訊。"""
import random

import discord
from discord import app_commands
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="測試機器人延遲")
    async def ping(self, interaction: discord.Interaction):
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong！延遲：{latency_ms}ms")

    @app_commands.command(name="roll", description="擲骰子，例如 2d6 代表擲兩顆六面骰")
    @app_commands.describe(dice="格式：NdM，例如 1d20、2d6")
    async def roll(self, interaction: discord.Interaction, dice: str = "1d6"):
        try:
            count_str, sides_str = dice.lower().split("d")
            count, sides = int(count_str or 1), int(sides_str)
            if not (1 <= count <= 100 and 2 <= sides <= 1000):
                raise ValueError
        except ValueError:
            await interaction.response.send_message(
                "格式錯誤，請用 NdM，例如 `2d6`（1-100 顆骰子，每顆 2-1000 面）", ephemeral=True
            )
            return

        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls)
        detail = ", ".join(map(str, rolls)) if count > 1 else str(rolls[0])
        await interaction.response.send_message(f"🎲 擲出：{detail}（總和：{total}）")

    @app_commands.command(name="coinflip", description="擲硬幣")
    async def coinflip(self, interaction: discord.Interaction):
        result = random.choice(["正面 🪙", "反面 🪙"])
        await interaction.response.send_message(result)

    @app_commands.command(name="8ball", description="問神奇8號球一個問題")
    @app_commands.describe(question="你的問題")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        answers = [
            "肯定是的。", "毫無疑問。", "看起來是這樣。", "很有可能。",
            "現在還不好說。", "再問一次吧。", "我不建議。", "回答是否定的。",
            "我的水晶球顯示為謎。", "別指望它。",
        ]
        await interaction.response.send_message(
            f"🎱 問題：{question}\n回答：{random.choice(answers)}"
        )

    @app_commands.command(name="userinfo", description="查看使用者資訊")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"{member.display_name} 的資訊", color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="使用者", value=str(member), inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(
            name="加入伺服器", value=discord.utils.format_dt(member.joined_at, "R"), inline=False
        )
        embed.add_field(
            name="帳號建立", value=discord.utils.format_dt(member.created_at, "R"), inline=False
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="查看伺服器資訊")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title=guild.name, color=discord.Color.blurple())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="成員數", value=guild.member_count, inline=True)
        embed.add_field(name="頻道數", value=len(guild.channels), inline=True)
        embed.add_field(name="擁有者", value=str(guild.owner), inline=True)
        embed.add_field(
            name="建立時間", value=discord.utils.format_dt(guild.created_at, "R"), inline=False
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
