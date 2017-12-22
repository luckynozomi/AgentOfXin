import discord
import asyncio
from discord.ext import commands
import platform
from discord_token import *
import subprocess
import sys

client = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)


@client.command()
async def hello():
    await client.say("Hello")


@client.command()
async def exec(*args):
    try:
        await client.say(subprocess.check_output(args))
    except:
        await client.say("Error: " + str(sys.exc_info()[0]))


@client.command()
async def temp():
    await client.say(subprocess.check_output(["vcgencmd", "measure_temp"]))




client.run(TOKEN)
