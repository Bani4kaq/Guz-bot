import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import re
import random
import shlex

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='?', intents=intents)

member_role = "member"


@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")


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

    deleted = await ctx.channel.purge(limit=amount)

    confirmation = await ctx.send(f"Deleted {len(deleted) - 1} messages.")
    await confirmation.delete(delay=3)


@mpurge.error
async def mpurge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("You don’t have permission to use this command (Manage Messages required).")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int, *, reason: str):
    try:
        timeout_duration = minutes * 60

        await member.timeout(duration=timeout_duration, reason=reason)

        await ctx.send(f"{member.mention} has been timed out for {minutes} minutes. Reason: {reason}")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("You don’t have permission to use this command (Timeout Memembers required).")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)