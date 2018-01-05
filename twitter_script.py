"""
This script is run everyday at 7 A.M. to check weather.
"""

import tweepy

from twitter_token import *
from WeatherForecast.weather import *


async def twitter_update_status(status):

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    api.update_status(status=status)


async def main(zip_code='32304', debug=False):
    """
    Everyday at 7 A.M., fetch weather forecast for the day and report it to discord server.
    Then report alerts, if there is any (defined in ParseForecast.report_alert() in WeatherForecast/weather.py), to
    twitter.
    :return: None
    """

    if debug is False:
        print_func = twitter_update_status
    else:
        print_func = myprint

    curr_time_and_zip = TimeAndZip(datetime_=datetime.now(), zip_code=zip_code)
    time_and_zip = curr_time_and_zip.day_lapse(day_delta=0)
    xml = await time_and_zip.fetch_forecast()
    forecast = ParseForecast(xml=xml)
    await forecast.report_alert(zip_code=curr_time_and_zip.zip_code,
                                date=curr_time_and_zip.datetime.date().isoformat(),
                                func=print_func)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(zip_code='32304', debug=False))
