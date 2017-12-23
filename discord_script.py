import discord
import asyncio
from discord.ext import commands
import platform
from discord_token import *
import subprocess
import sys

from weather import *

CHANNEL_ID = '354808585374531604'

client = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
#    subprocess.call(("python3", "CPUTempMon/TempMon", "30"))


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


@client.command()
async def log(*args):

    arg = args[0]
    if arg == 'temp':
        f = open('nohup.out')
        await client.say(f.read())
        f.close()


@client.command()
async def weather(*args):

    time_and_zip = TimeAndZip(zipcode=args[0]).next_day()
    test = WeatherForecast(time_and_zip.next_day())
    await test.report_weather()


client.run(TOKEN)
