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


async def myprint(*args):
    print(*args)
    return 0


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

        else:

            forecast = await self._dl_forecast(trials=trials)

            make_sure_path_exists(path)
            f = open(path + self.datetime.date().isoformat(), 'w')
            f.write(forecast)
            f.close()

        return forecast


class ParseForecast:

    def __init__(self, xml):
        """

        :param xml: xml file containing weather forecast

        """

        self.xml = xml

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

    async def report(self, zipcode, date, func=myprint):

        await func("On " + date + " in " + zipcode + ", low temp is " + str(self.low_temp) +
                   " degrees F, high temp is " + str(self.high_temp) + " degrees F, with a " + str(self.precipitation) +
                   "% chance of precipitation.")

        if self.hazard_flag is True:
            await func("There is a " + self.hazard_type + " " + self.hazard_pheno + " hazard " + self.hazard_sign +
                       " in your area.")
            await func("visit" + self.hazard_url + "for detailed info.")

    async def report_alert(self, zipcode, date, func=myprint):

        if self.precipitation > 40:
            await func("Today's chance of precipitation is " + str(self.precipitation) + "%. Please beware!")

        if self.hazard_flag is True:
            await func("There is a " + self.hazard_type + " " + self.hazard_pheno + " hazard " +
                       self.hazard_sign + " in your area.")
            await func("visit " + self.hazard_url + " for detailed info.")

        curr_date = dt.date(year=int(date[0:4]), month=int(date[5:7]), day=int(date[8:10]))
        delta = dt.timedelta(days=1)
        old_date = curr_date - delta
        path = "WeatherForecast/log/" + zipcode + "/"

        if os.path.isfile(path + old_date.isoformat()) is True:
            f = open(path + old_date.isoformat(), 'r')
            xml_past = f.read()
            f.close()

            forecast_past = ParseForecast(xml_past)

            if self.high_temp - 10.0 > forecast_past.high_temp or \
                    self.low_temp - 10.0 > forecast_past.low_temp:
                temp_alert = "warmer"
            elif self.high_temp + 10.0 < forecast_past.high_temp or \
                    self.low_temp + 10.0 < forecast_past.low_temp:
                temp_alert = "colder"
            else:
                temp_alert = "None"

            if temp_alert != "None":
                await func("Today's temperature is " + str(self.low_temp) + " to " +
                           str(self.high_temp) + " degrees F, which is much " + temp_alert +
                           " than yesterday.")


async def main():

    zipcode = '32304'

    current_datetime = datetime.now()
    time_and_zipp = TimeAndZip(zipcode=zipcode, datetime=current_datetime).day_lapse(day_delta=0)
    xml = await time_and_zipp.fetch_forecast()

    forecast = ParseForecast(xml=xml)
    # await forecast.report(zipcode=zipcode, date=current_datetime.date().isoformat())
    await forecast.report_alert(zipcode=zipcode, date=current_datetime.date().isoformat())


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
