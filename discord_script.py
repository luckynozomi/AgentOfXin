from discord.ext import commands
from discord_token import *
import subprocess
import sys
import logging

from WeatherForecast.weather import *
from WeatherForecast.tweet_alert import *

# set up discord
client = commands.Bot(command_prefix='!')

# set up logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=DIR_PATH + '/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


def get_channel(client, channel_name):
    for channel in client.get_all_channels():
        if channel.name == channel_name:
            return channel
    return None


async def print_discord(string, channel='general'):
    dest_channel = get_channel(client, channel)
    await client.send_message(dest_channel, string)
    return 0


async def check_weather_daily():
    """
    Everyday at 7 A.M., fetch weather forecast for the day and report it to discord server.
    Then report alerts, if there is any (defined in ParseForecast.report_alert() in WeatherForecast/weather.py), to
    twitter.
    :return: None
    """

    await client.wait_until_ready()

    curr_time_and_zip = TimeAndZip()

    if curr_time_and_zip.datetime.hour < 7:
        next_time_and_zip = curr_time_and_zip.day_lapse(day_delta=0)
    else:
        next_time_and_zip = curr_time_and_zip.day_lapse(day_delta=1)

    while True:

        timedelta = next_time_and_zip.datetime - curr_time_and_zip.datetime
        await asyncio.sleep(timedelta.total_seconds())

        curr_time_and_zip = next_time_and_zip

        xml = await curr_time_and_zip.fetch_forecast()
        forecast = ParseForecast(xml=xml)
        await forecast.report(zipcode=curr_time_and_zip.zipcode, date=curr_time_and_zip.datetime.date().isoformat(),
                              func=print_discord)
        await forecast.report_alert(zipcode=curr_time_and_zip.zipcode,
                                    date=curr_time_and_zip.datetime.date().isoformat(),
                                    func=twitter_update_status)
        next_time_and_zip = curr_time_and_zip.day_lapse(day_delta=1)


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
#    subprocess.call(("python3", "CPUTempMon/TempMon", "30"))


@client.command()
async def hello():

    await print_discord("Hello")


@client.command()
async def exe(*args):

    try:
        await print_discord(subprocess.check_output(args))
    except:
        await print_discord("Error: " + str(sys.exc_info()[0]))


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
    Command !weather zip_code returns the weather forecast in (zipcode) in today(if it's before 7 P.M.) or tomorrow
    (if it's after 7 P.M.)
    :param args: zipcode
    :return: none
    """
    day_delta = 1
    if datetime.now().hour < 19:
        day_delta = 0

    time_and_zip = TimeAndZip(zipcode=args[0]).day_lapse(day_delta=day_delta)
    xml = await time_and_zip.fetch_forecast()
    forecast = ParseForecast(xml=xml)
    await forecast.report(zipcode=args[0], date=time_and_zip.datetime.date().isoformat(), func=print_discord)

client.loop.create_task(check_weather_daily())
client.run(TOKEN)
