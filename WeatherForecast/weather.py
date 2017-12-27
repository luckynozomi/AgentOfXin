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

        return url

    def forecast_datetime(self, day_delta=0):

        forecast_datetime = self.datetime + dt.timedelta(days=day_delta)

        forecast_datetime = forecast_datetime.replace(hour=7, minute=0, second=0, microsecond=0)

        return TimeAndZip(datetime=forecast_datetime, zipcode=self.zipcode)


class WeatherForecast:

    def __init__(self, time_and_zip, trials=5):
        """

        :param time_and_zip: TimeAndZip object
        :param trials: number of attempts to reach server

        """

        self.high_temp = None
        self.low_temp = None
        self.precipitation = None
        self.hazard_flag = False
        self.hazard_pheno = None
        self.hazard_sign = None
        self.hazard_type = None
        self.hazard_url = None
        self.time_and_zip = time_and_zip
        self.forecast_url = time_and_zip.get_url()
        self.trials = trials
        self.forecast = None
        self.server_res_code = 504

        print(self.forecast_url)

    async def fetch_forecast(self):

        path = "WeatherForecast/log/" + self.time_and_zip.zipcode + "/"

        if os.path.isfile(path + self.time_and_zip.datetime.date().isoformat()) is True:

            f = open(path + self.time_and_zip.datetime.date().isoformat(), 'r')
            self.forecast = f.read()
            f.close()
            print("Opened File.")

        else:

            trial = 1

            while trial <= self.trials and self.server_res_code != 200:

                async with aiohttp.ClientSession() as session:
                    [self.server_res_code, self.forecast] = await fetch(session, self.forecast_url)

            if trial >= self.trials:
                raise ConnectionError

            print("Downloaded file.")

    def weather_condition(self):

        vals = parseString(self.forecast)

        path = "WeatherForecast/log/" + self.time_and_zip.zipcode + "/"
        make_sure_path_exists(path)

        f = open(path + self.time_and_zip.datetime.date().isoformat(), 'w')
        f.write(self.forecast)
        f.close()

        temp = vals.getElementsByTagName("value")
        self.high_temp = float(temp[0].childNodes[0].nodeValue)
        self.low_temp = float(temp[1].childNodes[0].nodeValue)
        self.precipitation = float(temp[2].childNodes[0].nodeValue)

        vals = parseString(self.forecast)

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

    async def report_weather(self):

        await self.fetch_forecast()
        self.weather_condition()

        print("Today, high temp is", self.high_temp, "F, low temp is", self.low_temp, "F, with a", self.precipitation,
              "chance of raining")

        if self.hazard_flag is True:

            print("There is a " + self.hazard_type + " " + self.hazard_pheno + " hazard " + self.hazard_sign +
                  " in your area")
            print("visit" + self.hazard_url + "for detailed info.")


async def temp_alert(weather_past, weather_now):

    if weather_now.high_temp - 10.0 > weather_past.high_temp or weather_now.low_temp - 10.0 > weather_past.low_temp:
        temp_alert = "warmer"
    elif weather_now.high_temp + 10.0 < weather_past.high_temp or weather_now.low_temp + 10.0 < weather_past.low_temp:
        temp_alert = "cooler"
    else:
        temp_alert = "None"

    return temp_alert


async def main():

    current_datetime = datetime.now()

    time_and_zipp = TimeAndZip(current_datetime)

    test = WeatherForecast(time_and_zipp.forecast_datetime(day_delta=0))

    await test.report_weather()

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
