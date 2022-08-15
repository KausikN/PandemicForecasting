"""
Other Parameters
"""

# Imports

# Classes
# Climate Classes
class Params_Climate:
    '''
    Class - Climate
    '''
    def __init__(self, 
        season, humidity, temperature, 
        **args
        ):
        # Current Season
        self.season = season
        # Current Humidity
        self.humidity = humidity
        # Current Temperature
        self.temperature = temperature
        # Other Arguments
        self.__dict__.update(args)