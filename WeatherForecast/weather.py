from xml.dom.minidom import parseString
from datetime import datetime
import datetime as dt
import aiohttp
import asyncio
import os
import errno


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


async def fetch(session, url):
    async with session.get(url) as response:
        return response.status, await response.text()


class TimeAndZip:

    def __init__(self, datetime=datetime.now(), duration=dt.timedelta(hours=12), zipcode='32304'):
        """

        :param datetime:  datetime object
        :param duration:  timedelta object
        :param zipcode:   5-digit string
        """

        self.datetime = datetime
        self.duration = duration
        self._datetime_end = datetime + duration

        if len(zipcode) != 5 or zipcode.isalnum() is False:
            raise ValueError

        self.zipcode = zipcode

    def get_url(self):
        """

        :return: string

        """

        url = "https://graphical.weather.gov" + \
              "/xml/sample_products/browser_interface/ndfdXMLclient.php?zipCodeList=" + self.zipcode + \
              "&product=time-series&begin=" + self.datetime.isoformat() + "&end=" + \
              self._datetime_end.isoformat() + "&maxt=maxt&mint=mint&pop12=pop12&wwa=wwa"

        print(url)
        return url

    def day_lapse(self, day_delta=0):
        """

        :param day_delta: int
        :return: TimeAndZip object whose time is X days after today at 7 AM.
        """

        forecast_datetime = self.datetime + dt.timedelta(days=day_delta)

        forecast_datetime = forecast_datetime.replace(hour=7, minute=0, second=0, microsecond=0)

        return TimeAndZip(datetime=forecast_datetime, zipcode=self.zipcode)

    async def _dl_forecast(self, trials=5):
        """

        :param trials: int
        :return: forecast XML file
        """

        trial = 1
        server_res_code = None
        forecast = None

        while trial <= trials and server_res_code != 200:
            async with aiohttp.ClientSession() as session:
                [server_res_code, forecast] = await fetch(session, self.get_url())

        if trial >= trials:
            raise ConnectionError

        return forecast

    async def fetch_forecast(self, trials=5):

        path = "WeatherForecast/log/" + self.zipcode + "/"

        if os.path.isfile(path + self.datetime.date().isoformat()) is True:

            f = open(path + self.datetime.date().isoformat(), 'r')
            forecast = f.read()
            f.close()
            print("Opened File.")

        else:

            forecast = await self._dl_forecast(trials=trials)
            print("Downloaded file.")

            make_sure_path_exists(path)
            f = open(path + self.datetime.date().isoformat(), 'w')
            f.write(forecast)
            f.close()

        return forecast


class WeatherForecast:

    def __init__(self, xml):
        """

        :param xml: xml file containing weather forecast

        """

        vals = parseString(xml)

        temp = vals.getElementsByTagName("value")
        self.high_temp = float(temp[0].childNodes[0].nodeValue)
        self.low_temp = float(temp[1].childNodes[0].nodeValue)
        self.precipitation = float(temp[2].childNodes[0].nodeValue)

        hazards = vals.getElementsByTagName("hazard-conditions")
        hazards = hazards[0]

        self.hazard_flag = hazards.hasChildNodes()

        if self.hazard_flag is True:
            hazard_info = hazards.getElementsByTagName("hazard")[0]
            self.hazard_pheno = hazard_info.attributes['phenomena'].nodeValue  # "Winter Weather"
            self.hazard_sign = hazard_info.attributes['significance'].nodeValue  # "Advisory"
            self.hazard_type = hazard_info.attributes['hazardType'].nodeValue  # "long duration"

            hazard_url = hazards.getElementsByTagName("hazardTextURL")
            self.hazard_url = hazard_url[0].childNodes[0].nodeValue

        vals.unlink()

    async def report(self, zipcode, date, func=print):

        await func("On " + date + " in " + zipcode + ", low temp is " + str(self.low_temp) +
                   " degrees F, high temp is " + str(self.high_temp) + " degrees F, with a " + str(self.precipitation) +
                   "% chance of precipitation.")

        if self.hazard_flag is True:
            print("There is a " + self.hazard_type + " " + self.hazard_pheno + " hazard " + self.hazard_sign +
                  " in your area.")
            print("visit" + self.hazard_url + "for detailed info.")


async def temp_alert(weather_past, weather_now):

    if weather_now.high_temp - 10.0 > weather_past.high_temp or weather_now.low_temp - 10.0 > weather_past.low_temp:
        alert = "warmer"
    elif weather_now.high_temp + 10.0 < weather_past.high_temp or weather_now.low_temp + 10.0 < weather_past.low_temp:
        alert = "cooler"
    else:
        alert = "None"

    return alert


async def main():

    current_datetime = datetime.now()

    time_and_zipp = TimeAndZip(current_datetime)

    xml = await time_and_zipp.fetch_forecast()

    forecast = WeatherForecast(xml=xml)

    await forecast.report(zipcode='32304', date=current_datetime.date().isoformat())

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
