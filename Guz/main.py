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
async def assign(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    role = discord.utils.get(ctx.guild.roles, name=member_role)

    if role:
        await member.add_roles(role)
        await ctx.send(f"{member.mention} is now {member_role}")
    else:
        await ctx.send("Role doesn't exist")


@bot.command()
async def remove(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    role = discord.utils.get(ctx.guild.roles, name=member_role)

    if role:
        await member.remove_roles(role)
        await ctx.send(f"{member_role} role has been removed from {member.mention}")
    else:
        await ctx.send("Role doesn't exist")


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
async def mpurge(ctx, amount: int):
    if amount < 1:
        await ctx.reply("Please provide a number greater than 0.")
        return
    if amount > 100:
        await ctx.reply("You can only delete up to 100 messages at once.")
        return

    deleted = await ctx.channel.purge(limit=amount + 1)

    confirmation = await ctx.send(f"Deleted {len(deleted) - 1} messages.")
    await confirmation.delete(delay=3)


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
