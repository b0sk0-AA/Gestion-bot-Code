import discord
from discord.ext import commands
import config

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="+", intents=intents)

@bot.event
async def on_ready():
    await bot.load_extension("cogs.moderation")
    await bot.load_extension("cogs.logs")
    await bot.load_extension("cogs.tickets")
    print(f"✅ Connecté en tant que {bot.user}")

bot.run(config.TOKEN)