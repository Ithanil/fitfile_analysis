from meteostat import Point, Hourly
from datetime import datetime

def get_weather_data(data):
# data needs to contain entries for timestamp, position_lat, positional_long and optionally altitude

    # extract time and location
    tstart = data['timestamp'][0]
    tstart = datetime(tstart.year, tstart.month, tstart.day, tstart.hour)

    if 'altitude' in data.keys():
        location = Point(data['position_lat'][0], data['position_long'][0], data['altitude'][0])
    else:
        location = Point(data['position_lat'][0], data['position_long'][0])

    # fetch weather
    weather_data = Hourly(location, tstart, tstart)
    weather_data = weather_data.fetch()

    return weather_data