from discord.ext import commands
from discord_token import *
import subprocess
import sys

from WeatherForecast.weather import *

CHANNEL_ID = '354808585374531604'
client = commands.Bot(command_prefix='!')


async def check_weather_daily():

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
        forecast = WeatherForecast(xml=xml)
        await forecast.report(zipcode=curr_time_and_zip.zipcode, date=curr_time_and_zip.datetime.date().isoformat(),
                              func=client.say)
        next_time_and_zip = curr_time_and_zip.next_day()


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
#    subprocess.call(("python3", "CPUTempMon/TempMon", "30"))


@client.command()
async def hello():

    await client.say("Hello")


@client.command()
async def exe(*args):

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

    day_delta = 1
    if datetime.now().hour < 19:
        day_delta = 0

    time_and_zip = TimeAndZip(zipcode=args[0]).day_lapse(day_delta=day_delta)
    xml = await time_and_zip.fetch_forecast()
    forecast = WeatherForecast(xml=xml)
    await forecast.report(zipcode=args[0], date=time_and_zip.datetime.date().isoformat(), func=client.say)

client.loop.create_task(check_weather_daily())
client.run(TOKEN)
