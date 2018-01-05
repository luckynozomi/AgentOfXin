from discord.ext import commands
from discord_token import *
import subprocess
import logging

from WeatherForecast.weather import *

# set up discord
client = commands.Bot(command_prefix='!')

# set up logging
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename=DIR_PATH + '/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


def get_channel(client_, channel_name):
    for channel in client_.get_all_channels():
        if channel.name == channel_name:
            return channel
    return None


async def print_discord(string, channel='general'):
    dest_channel = get_channel(client, channel)
    await client.send_message(dest_channel, string)
    return 0


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
#    subprocess.call(("python3", "CPUTempMon/TempMon", "30"))


@client.command()
async def hello():

    await print_discord("Hello")


@client.command()
async def temp():

    await print_discord(subprocess.check_output(["vcgencmd", "measure_temp"]))


@client.command()
async def log(*args):

    arg = args[0]
    if arg == 'temp':
        f = open('nohup.out')
        await print_discord(f.read())
        f.close()


@client.command()
async def weather(*args):
    """
    Command !weather zip_code returns the weather forecast in (zip_code) in today(if it's before 7 P.M.) or tomorrow
    (if it's after 7 P.M.)
    :param args: zip_code
    :return: none
    """
    day_delta = 1
    dt_now = datetime.now()
    if dt_now.hour < 19:
        day_delta = 0

    time_and_zip = TimeAndZip(datetime_=dt_now, zip_code=args[0]).day_lapse(day_delta=day_delta)
    await client.say(dt_now.isoformat())     # debug use
    xml = await time_and_zip.fetch_forecast()
    forecast = ParseForecast(xml=xml)
    await forecast.report(zip_code=args[0], date=time_and_zip.datetime.date().isoformat(), func=print_discord)

client.run(TOKEN)
