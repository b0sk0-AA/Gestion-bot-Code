import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="Aucune raison fournie"):
        await member.ban(reason=reason)
        await ctx.send(f"🔨 **{member}** a été banni. Raison : {reason}")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="Aucune raison fournie"):
        await member.kick(reason=reason)
        await ctx.send(f"👢 **{member}** a été kick. Raison : {reason}")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, *, reason="Aucune raison fournie"):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            await ctx.send("❌ Le rôle **Muted** n'existe pas sur ce serveur !")
            return
        await member.add_roles(role, reason=reason)
        await ctx.send(f"🔇 **{member}** a été mute. Raison : {reason}")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason="Aucune raison fournie"):
        await ctx.send(f"⚠️ **{member}** a été averti. Raison : {reason}")
        try:
            await member.send(f"⚠️ Tu as reçu un avertissement sur **{ctx.guild.name}**.\nRaison : {reason}")
        except:
            await ctx.send("*(Impossible d'envoyer un MP à ce membre)*")

async def setup(bot):
    await bot.add_cog(Moderation(bot))