import requests
from xml.dom.minidom import parseString
from datetime import datetime
import datetime as dt
import sys



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


    def get_URL(self):
        """

        :return: string

        """

        URL = "https://graphical.weather.gov" + \
              "/xml/sample_products/browser_interface/ndfdXMLclient.php?zipCodeList=" + self.zipcode + \
              "&product=time-series&begin=" + self.datetime.isoformat() + "&end=" + \
              self._datetime_end.isoformat() + "&maxt=maxt&mint=mint&pop12=pop12&wwa=wwa"

        return URL


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
        self.hazard_URL = None

        self.server_res_code = 504
        while trials > 0 and self.server_res_code != 200:
            self.forecast = requests.get(time_and_zip.get_URL())
            self.server_res_code = self.forecast.status_code

        if trials == 0:
            raise ConnectionError

    def weather_condition(self):

        vals = parseString(self.forecast.text)

        temp = vals.getElementsByTagName("value")
        self.high_temp = float(temp[0].childNodes[0].nodeValue)
        self.low_temp = float(temp[1].childNodes[0].nodeValue)
        self.precipitation = float(temp[2].childNodes[0].nodeValue)

        vals.unlink()

    def hazard_condition(self):

        vals = parseString(self.forecast.text)

        hazards = vals.getElementsByTagName("hazard-conditions")
        hazards = hazards[0]

        self.hazard_flag = hazards.hasChildNodes()

        if self.hazard_flag is True:
            hazard_info = hazards.getElementsByTagName("hazard")[0]
            self.phenomena = hazard_info.attributes['phenomena'].nodeValue  # "Winter Weather"
            self.significance = hazard_info.attributes['significance'].nodeValue  # "Advisory"
            self.hazard_type = hazard_info.attributes['hazardType'].nodeValue  # "long duration"

            hazard_URL = hazards.getElementsByTagName("hazardTextURL")
            self.hazard_URL = hazard_URL[0].childNodes[0].nodeValue

        vals.unlink()


    def report_weather(self):

        self.weather_condition()
        self.hazard_condition()

        print("Today, high temp is", self.high_temp, "F, low temp is", self.low_temp, "F, with a", self.precipitation, "chance of raining")

        if self.hazard_flag is True:

            print("There is a " + self.hazard_type + " " + self.phenomena + " hazard " + self.significance + " in your area")
            print("visit" + self.hazard_URL + "for detailed info.")


if __name__ == "__main__":

    current_datetime = datetime.now()

    if current_datetime.hour > 19:
        delta = dt.timedelta(days=1)
        current_datetime = current_datetime + delta

    forecast_datetime = current_datetime.replace(hour=7, minute=0, second=0, microsecond=0)

    time_and_zip = TimeAndZip(forecast_datetime)

    test = WeatherForecast(time_and_zip)

    test.report_weather()
