import discord
from discord.ext import commands
import config

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── MESSAGES ──────────────────────────────────────
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        channel = message.guild.get_channel(config.LOGS_MESSAGES_ID)
        if not channel:
            return
        embed = discord.Embed(title="🗑️ Message supprimé", color=discord.Color.red())
        embed.add_field(name="Auteur", value=message.author.mention)
        embed.add_field(name="Salon", value=message.channel.mention)
        embed.add_field(name="Message", value=message.content or "*(vide)*", inline=False)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        channel = before.guild.get_channel(config.LOGS_MESSAGES_ID)
        if not channel:
            return
        embed = discord.Embed(title="✏️ Message modifié", color=discord.Color.orange())
        embed.add_field(name="Auteur", value=before.author.mention)
        embed.add_field(name="Salon", value=before.channel.mention)
        embed.add_field(name="Avant", value=before.content or "*(vide)*", inline=False)
        embed.add_field(name="Après", value=after.content or "*(vide)*", inline=False)
        await channel.send(embed=embed)

    # ── MEMBRES ───────────────────────────────────────
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.get_channel(config.LOGS_MEMBRES_ID)
        if not channel:
            return
        embed = discord.Embed(title="📥 Nouveau membre", color=discord.Color.green())
        embed.add_field(name="Membre", value=member.mention)
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = member.guild.get_channel(config.LOGS_MEMBRES_ID)
        if not channel:
            return
        embed = discord.Embed(title="📤 Membre parti", color=discord.Color.red())
        embed.add_field(name="Membre", value=str(member))
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

    # ── MODÉRATION ────────────────────────────────────
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        channel = guild.get_channel(config.LOGS_MODERATION_ID)
        if not channel:
            return
        embed = discord.Embed(title="🔨 Membre banni", color=discord.Color.dark_red())
        embed.add_field(name="Membre", value=str(user))
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        channel = guild.get_channel(config.LOGS_MODERATION_ID)
        if not channel:
            return
        embed = discord.Embed(title="✅ Membre débanni", color=discord.Color.green())
        embed.add_field(name="Membre", value=str(user))
        await channel.send(embed=embed)

    # ── SALONS ────────────────────────────────────────
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        logs = channel.guild.get_channel(config.LOGS_SALONS_ID)
        if not logs:
            return
        embed = discord.Embed(title="✅ Salon créé", color=discord.Color.green())
        embed.add_field(name="Salon", value=channel.mention)
        embed.add_field(name="Type", value=str(channel.type))
        await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        logs = channel.guild.get_channel(config.LOGS_SALONS_ID)
        if not logs:
            return
        embed = discord.Embed(title="🗑️ Salon supprimé", color=discord.Color.red())
        embed.add_field(name="Nom", value=channel.name)
        embed.add_field(name="Type", value=str(channel.type))
        await logs.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Logs(bot))