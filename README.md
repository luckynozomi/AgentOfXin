## General
Python3 script, not compatible with python2.

discord_script.py is the script for setting up the discord server and push notifications to twitter.

WeatherForecast/weather.py is the main script for fetching weather forecast and generating alerts.

## Notification rule
Push an twitter notification each day at 7 A.M. if the weather report today(7A.M - 7 P.M.) indicates that:
1) there is a temperature change of more than 10°F than yesterday;
OR
2) today has a >40% chance of precipitation;
OR
3) there is an issued Weather Advisory/Warning/Watch.

## Relevant Documentation

### discord.py
http://discordpy.readthedocs.io/en/latest/index.html

### tweepy
http://docs.tweepy.org/en/v3.5.0/

### NDFD REST web service
https://graphical.weather.gov/xml/rest.php
