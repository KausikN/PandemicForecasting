'''
Custom Parameter Classes
'''

# Imports

# Classes
# Climate Classes
class ClimateParameters:
    def __init__(self, season, humidity, temperature):
        self.season = season                                            # Current Season
        self.humidity = humidity                                        # Current Humidity
        self.temperature = temperature                                  # Current Temperature