import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import re
import random
import shlex
import asyncio
from datetime import timedelta

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='?', intents=intents)

member_role = "member"


@bot.event
async def on_ready():
    print("It's adventure time!")


@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    cleaned = re.sub(r"<@!?\d+>|<@&\d+>", "", message.content)

    if (
        message.attachments or
        message.content.startswith("https://cdn.discordapp.com/attachments/") or
        "http" in message.content
    ):
        return

    if "dancho" in message.content.lower():
        await message.channel.send(f"{message.author.mention} W DANCHO")

    if "67" in cleaned:
        await message.reply("https://tenor.com/view/67-67-kid-edit-analog-horror-phonk-gif-3349401281762803381")

    await bot.process_commands(message)


@bot.command()
@commands.has_permissions(manage_roles=True)
async def assign(ctx, member: discord.Member = None, *, role_name: str = None):
    if member is None:
        member = ctx.author

    if role_name is None:
        role_name = member_role

    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role is None:
        match = re.match(r"<@&(\d+)>", role_name)
        if match:
            role = ctx.guild.get_role(int(match.group(1)))

    if role is None:
        await ctx.send("Role not found.")
        return

    try:
        await member.add_roles(role)
        await ctx.send(f"{role.mention} assigned to {member.mention}")
    except discord.Forbidden:
        await ctx.send("I don't have permission to assign that role.")
    except discord.HTTPException as e:
        await ctx.send(f"Discord API error: {e}")


@assign.error
async def assign_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("You don’t have permission to use this command (Manage Roles required).")


@bot.command()
@commands.has_permissions(manage_roles=True)
async def remove(ctx, member: discord.Member = None, *, role_name: str = None):
    if member is None:
        member = ctx.author

    if role_name is None:
        role_name = member_role

    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role is None:
        match = re.match(r"<@&(\d+)>", role_name)
        if match:
            role = ctx.guild.get_role(int(match.group(1)))

    if role is None:
        await ctx.send("Role not found.")
        return

    try:
        await member.remove_roles(role)
        await ctx.send(f"Removed {role.mention} from {member.mention}")
    except discord.Forbidden:
        await ctx.send("I don't have permission to remove that role.")
    except discord.HTTPException as e:
        await ctx.send(f"Something went wrong: {e}")


@remove.error
async def remove_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("You don’t have permission to use this command (Manage Roles required).")


@bot.command()
async def choose(ctx, *, options):
    try:
        parts = shlex.split(options)
    except ValueError:
        await ctx.reply("There was an error parsing your options. Make sure your quotes are balanced!")
        return

    if len(parts) < 2:
        await ctx.reply("Please provide at least two options to choose from!")
        return

    choice = random.choice(parts)

    embed = discord.Embed(
        description=f"``{choice}``",
        color=discord.Color.green()
    )

    await ctx.reply(embed=embed)


@bot.command()
@commands.has_permissions(manage_messages=True)
async def mpurge(ctx, amount: int):
    if amount < 1:
        await ctx.reply("Please provide a number greater than 0.")
        return
    if amount > 100:
        await ctx.reply("You can only delete up to 100 messages at once.")
        return

    deleted = await ctx.channel.purge(limit=1 + amount)

    confirmation = await ctx.send(f"Deleted {len(deleted) - 1} messages.")
    await confirmation.delete(delay=3)


@mpurge.error
async def mpurge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("You don’t have permission to use this command (Manage Messages required).")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int, *, reason: str):
    timeout_duration = timedelta(minutes=minutes)
    await member.timeout(timeout_duration, reason=reason)

    embed = discord.Embed(
        title=f"{member.display_name} has been muted",
        color=discord.Color.red()
    )
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Duration", value=f"{minutes} minutes", inline=False)
    embed.set_footer(text=f"Muted by {ctx.author.display_name}")

    await ctx.send(embed=embed)


@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("You don’t have permission to use this command (Timeout Memembers required).")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    try:
        await member.timeout(None, reason=reason)

        embed = discord.Embed(
            title=f"{member.display_name} has been unmuted",
            color=discord.Color.green()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text=f"Unmuted by {ctx.author.display_name}")

        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.reply("I don't have permission to unmute that user.")
    except discord.HTTPException as e:
        await ctx.reply(f"Something went wrong while unmuting: {e}")


@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("You don’t have permission to use this command (Timeout Members required).")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("Usage: `?unmute @user [reason]`")


@bot.command(aliases=['rm'])
async def reminder(ctx, time: str = None, *, text: str = None):
    if time is None:
        await ctx.reply("Please specify a duration (e.g. `?rm 10m`, `?rm 2h`, or `?rm 1d`).")
        return

    if text is None:
        text = "something"

    match = re.match(r"^(\d+)([mhd])$", time.lower())
    if not match:
        await ctx.reply("Invalid time format. Use something like `10m`, `2h`, or `1d`.")
        return

    amount, unit = match.groups()
    amount = int(amount)

    delay = 0
    unit_full = ""

    if unit == "m":
        delay = amount * 60
        unit_full = "minute" if amount == 1 else "minutes"
    elif unit == "h":
        delay = amount * 60 * 60
        unit_full = "hour" if amount == 1 else "hours"
    elif unit == "d":
        delay = amount * 60 * 60 * 24
        unit_full = "day" if amount == 1 else "days"
    else:
        await ctx.reply("Invalid time unit. Use m, h, or d.")
        return

    embed = discord.Embed(
        title="Reminder Set",
        description=f"{ctx.author.mention}, I will remind you in **{amount} {unit_full}** about **{text}**.",
        color=discord.Color.green()
    )
    embed.set_footer(text="Reminder bot")
    await ctx.send(embed=embed)

    await asyncio.sleep(delay)

    try:
        await ctx.author.send(f"Hey, you asked me to remind you about {text}.")
    except discord.Forbidden:
        await ctx.send(f"{ctx.author.mention}, I couldn’t DM you your reminder (your DMs might be closed).")


class ChannelNameModal(discord.ui.Modal, title="Edit Channel Name"):
    name = discord.ui.TextInput(
        label="Channel Name",
        placeholder="Letters and numbers only",
        max_length=50
    )

    def __init__(self, view):
        super().__init__()
        self.view_ref = view

    async def on_submit(self, interaction: discord.Interaction, /):
        if not re.fullmatch(r"[A-Za-z0-9 ]+", self.name.value):
            await interaction.response.send_message(
                "❌ Channel name can only contain letters and numbers.",
                ephemeral=True
            )
            return

        self.view_ref.channel_name = self.name.value
        await interaction.response.edit_message(
            embed=self.view_ref.build_embed(),
            view=self.view_ref
        )


class UserLimitModal(discord.ui.Modal, title="Edit User Limit"):
    limit = discord.ui.TextInput(
        label="User Limit (1–10)",
        placeholder="Enter a number",
        max_length=2
    )

    def __init__(self, view):
        super().__init__()
        self.view_ref = view

    async def on_submit(self, interaction: discord.Interaction, /):
        if not self.limit.value.isdigit():
            await interaction.response.send_message(
                "❌ User limit must be a number.",
                ephemeral=True
            )
            return

        value = int(self.limit.value)
        if value < 1 or value > 10:
            await interaction.response.send_message(
                "❌ User limit must be between 1 and 10.",
                ephemeral=True
            )
            return

        self.view_ref.user_limit = str(value)
        await interaction.response.edit_message(
            embed=self.view_ref.build_embed(),
            view=self.view_ref
        )


class PrivacySelect(discord.ui.Select):
    def __init__(self, view):
        self.view_ref = view
        options = [
            discord.SelectOption(label="Public", emoji="🔓"),
            discord.SelectOption(label="Private", emoji="🔒")
        ]
        super().__init__(placeholder="Select privacy", options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view_ref.privacy = self.values[0]
        await interaction.response.edit_message(
            embed=self.view_ref.build_embed(),
            view=self.view_ref
        )


class VCCreationView(discord.ui.View):
    def __init__(self, author: discord.Member):
        super().__init__(timeout=120)
        self.author = author

        self.channel_name = f"{author.name}'s VC"
        self.user_limit = "Unlimited"
        self.privacy = "Public"

        self.add_item(PrivacySelect(self))

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        return interaction.user == self.author

    def build_embed(self):
        embed = discord.Embed(
            title="Temporary Voice Channel",
            description=(
                "Customize your temporary voice channel below.\n"
                "It will be deleted automatically when everyone leaves."
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="🏷️ Channel Name",
            value=self.channel_name,
            inline=False
        )

        embed.add_field(
            name="👥 User Limit",
            value=self.user_limit,
            inline=False
        )

        embed.add_field(
            name="🔒 Privacy",
            value=self.privacy,
            inline=False
        )

        embed.set_footer(text="Use the buttons below to edit these options.")
        return embed

    @discord.ui.button(label="Edit Name", style=discord.ButtonStyle.primary)
    async def edit_name(self, interaction: discord.Interaction, _button: discord.ui.Button):
        await interaction.response.send_modal(ChannelNameModal(self))

    @discord.ui.button(label="Edit User Limit", style=discord.ButtonStyle.primary)
    async def edit_limit(self, interaction: discord.Interaction, _button: discord.ui.Button):
        await interaction.response.send_modal(UserLimitModal(self))

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, _button: discord.ui.Button):
        await interaction.response.send_message(
            "✅ Confirm pressed (no functionality yet).",
            ephemeral=True
        )


@bot.command(name="vc", aliases=["voice", "voicechannel"])
async def vc(ctx: commands.Context):
    view = VCCreationView(ctx.author)
    await ctx.send(embed=view.build_embed(), view=view)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
