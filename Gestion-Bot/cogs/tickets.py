import discord
from discord.ext import commands
import config
import asyncio


# ── MODAL OUVERTURE ───────────────────────────────────
class OpenTicketModal(discord.ui.Modal, title="📩 Ouvrir un ticket"):
    reason = discord.ui.TextInput(
        label="Raison",
        placeholder="Explique ton problème...",
        style=discord.TextStyle.long,
        min_length=10,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        reason = self.reason.value

        existing = discord.utils.get(guild.text_channels, name=f"ticket-{member.name.lower()}")
        if existing:
            await interaction.response.send_message(f"❌ Tu as déjà un ticket ouvert : {existing.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{member.name.lower()}",
            overwrites=overwrites,
            reason=f"Ticket ouvert par {member}"
        )

        embed = discord.Embed(
            title="🎫 Ticket ouvert",
            description=f"Bonjour {member.mention} ! Le staff va te répondre dès que possible.",
            color=discord.Color.blurple()
        )
        embed.add_field(name="📋 Raison", value=reason, inline=False)
        embed.set_image(url="attachment://banner.png")

        file = discord.File("banner.png", filename="banner.png")
        await channel.send(embed=embed, file=file, view=TicketActionsView())
        await interaction.response.send_message(f"✅ Ton ticket a été créé : {channel.mention}", ephemeral=True)

        logs = guild.get_channel(config.LOGS_TICKETS_ID)
        if logs:
            log_embed = discord.Embed(title="🎫 Ticket ouvert", color=discord.Color.green())
            log_embed.add_field(name="Membre", value=member.mention)
            log_embed.add_field(name="Salon", value=channel.mention)
            log_embed.add_field(name="Raison", value=reason, inline=False)
            await logs.send(embed=log_embed)


# ── MODAL FERMETURE ───────────────────────────────────
class CloseTicketModal(discord.ui.Modal, title="🔒 Fermer le ticket"):
    reason = discord.ui.TextInput(
        label="Raison de fermeture",
        placeholder="Problème résolu, spam, etc...",
        style=discord.TextStyle.long,
        min_length=5,
        max_length=500
    )

    def __init__(self, claimed_by=None):
        super().__init__()
        self.claimed_by = claimed_by

    async def on_submit(self, interaction: discord.Interaction):
        member = interaction.user
        channel = interaction.channel
        reason = self.reason.value

        await interaction.response.send_message(f"🔒 Fermeture du ticket dans 3 secondes...\n📋 Raison : {reason}")

        logs = interaction.guild.get_channel(config.LOGS_TICKETS_ID)
        if logs:
            log_embed = discord.Embed(title="🔒 Ticket fermé", color=discord.Color.red())
            log_embed.add_field(name="Fermé par", value=member.mention)
            log_embed.add_field(name="Salon", value=channel.name)
            log_embed.add_field(name="Raison", value=reason, inline=False)
            if self.claimed_by:
                log_embed.add_field(name="Était claim par", value=f"<@{self.claimed_by}>")
            await logs.send(embed=log_embed)

        await asyncio.sleep(3)
        await channel.delete()


# ── BOUTON OUVERTURE ──────────────────────────────────
class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Ouvrir un ticket", style=discord.ButtonStyle.blurple, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(OpenTicketModal())


# ── BOUTONS CLAIM & FERMETURE ─────────────────────────
class TicketActionsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.claimed_by = None

    @discord.ui.button(label="✋ Claim", style=discord.ButtonStyle.green, custom_id="claim_ticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user

        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("❌ Tu n'as pas la permission de claim ce ticket !", ephemeral=True)
            return

        if self.claimed_by:
            await interaction.response.send_message(f"❌ Ce ticket est déjà claim par <@{self.claimed_by}> !", ephemeral=True)
            return

        self.claimed_by = member.id
        button.disabled = True
        button.label = f"✋ Claim par {member.name}"
        await interaction.response.edit_message(view=self)
        await interaction.channel.send(f"✅ {member.mention} a **claim** ce ticket et va s'en occuper !")

        logs = interaction.guild.get_channel(config.LOGS_TICKETS_ID)
        if logs:
            log_embed = discord.Embed(title="✋ Ticket claim", color=discord.Color.yellow())
            log_embed.add_field(name="Staff", value=member.mention)
            log_embed.add_field(name="Salon", value=interaction.channel.mention)
            await logs.send(embed=log_embed)

    @discord.ui.button(label="🔒 Fermer", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CloseTicketModal(claimed_by=self.claimed_by))


# ── COG ───────────────────────────────────────────────
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(TicketButton())
        bot.add_view(TicketActionsView())

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def panel(self, ctx):
        channel = ctx.guild.get_channel(config.TICKET_PANEL_ID)
        if not channel:
            await ctx.send("❌ Salon introuvable, vérifie ton `TICKET_PANEL_ID` dans config.py")
            return
        embed = discord.Embed(
            title="🎫 Support",
            description="Tu as besoin d'aide ? Clique sur le bouton ci-dessous pour ouvrir un ticket !",
            color=discord.Color.blurple()
        )
        await channel.send(embed=embed, view=TicketButton())
        await ctx.send(f"✅ Panel envoyé dans {channel.mention} !")

async def setup(bot):
    await bot.add_cog(Tickets(bot))