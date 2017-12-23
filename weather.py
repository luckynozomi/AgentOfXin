import requests
from xml.dom.minidom import parseString
from datetime import datetime
import datetime as dt
import sys

FORECAST_RANGE = dt.timedelta(hours=12)
#ZIP_CODE = '04005'
#ZIP_CODE = '32304'
ZIP_CODE = sys.argv[1]

current_datetime = datetime.now()
forecast_datetime = current_datetime

if current_datetime.hour > 19:
    delta = dt.timedelta(days=1)
    forecast_datetime = current_datetime + delta

forecast_datetime = forecast_datetime.replace(hour=7, minute=0, second=0, microsecond=0)
forecast_datetime_end = forecast_datetime + FORECAST_RANGE


URL = "https://graphical.weather.gov/" \
      "xml/sample_products/browser_interface/ndfdXMLclient.php?zipCodeList=" + ZIP_CODE + \
      "&product=time-series&begin=" + forecast_datetime.isoformat() + "&end=" + forecast_datetime_end.isoformat() + \
      "&maxt=maxt&mint=mint&pop12=pop12&wwa=wwa"

trials = 5
response = 504
while trials > 0 and response == 504:
    test = requests.get(URL)
    response = test.status_code

if trials == 0:
    raise ConnectionError

vals = parseString(test.text)

temp = vals.getElementsByTagName("value")
high_temp = float(temp[0].childNodes[0].nodeValue)
low_temp = float(temp[1].childNodes[0].nodeValue)
prob = float(temp[2].childNodes[0].nodeValue)

print("Today, high temp is", high_temp, "F, low temp is", low_temp, "F, with a", prob, "chance of raining")

hazards = vals.getElementsByTagName("hazard-conditions")
hazards = hazards[0]

if hazards.hasChildNodes() == True:

    hazard_info = hazards.getElementsByTagName("hazard")[0]
    phenomena = hazard_info.attributes['phenomena'].nodeValue # "Winter Weather"
    significance = hazard_info.attributes['significance'].nodeValue # "Advisory"
    hazard_type = hazard_info.attributes['hazardType'].nodeValue # "long duration"

    hazard_URL = hazards.getElementsByTagName("hazardTextURL")
    hazard_URL = hazard_URL[0].childNodes[0].nodeValue

    print("There is a " + hazard_type + " " + phenomena + " hazard " + significance + " in your area")
    print("visit" + hazard_URL "for detailed info.")

vals.unlink()
