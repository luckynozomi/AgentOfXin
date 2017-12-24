from discord.ext import commands
from discord_token import *
import subprocess

from WeatherForecast.weather import *

CHANNEL_ID = '354808585374531604'

client = commands.Bot(command_prefix='!')


async def check_weather_daily():

    await client.wait_until_ready()

    curr_time_and_zip = TimeAndZip()

    if curr_time_and_zip.datetime.hour < 7:
        next_time_and_zip = curr_time_and_zip
        next_time_and_zip.datetime.replace(hour=7, minute=0, second=0, microsecond=0)
    else:
        next_time_and_zip = curr_time_and_zip.next_day()

    while True:

        timedelta = next_time_and_zip.datetime - curr_time_and_zip.datetime

        await asyncio.sleep(timedelta.total_seconds())

        curr_time_and_zip = next_time_and_zip

        weather = WeatherForecast(curr_time_and_zip)
        await weather.report_weather()
        await client.say("Current Temp in " + str(curr_time_and_zip.zipcode) + " is " + str(weather.low_temp) + "to" +
                         str(weather.high_temp) + " degrees F, with " + str(weather.precipitation) +
                         "% chance of precipitation.")
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

    time_and_zip = TimeAndZip(zipcode=args[0]).next_day()
    chk_weather = WeatherForecast(time_and_zip.next_day())
    await chk_weather.report_weather()
    await client.say("Current Temp in " + str(time_and_zip.zipcode) + " is " + str(chk_weather.low_temp) + " to " +
                     str(chk_weather.high_temp) + " degrees F, with " + str(chk_weather.precipitation) +
                     "% chance of precipitation.")

client.loop.create_task(check_weather_daily())
client.run(TOKEN)
