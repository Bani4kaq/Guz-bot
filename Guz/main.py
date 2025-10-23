import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

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

    if "dancho" in message.content.lower():
        await message.channel.send(f"{message.author.mention} W DANCHO")

    if "67" in message.content:
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

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
