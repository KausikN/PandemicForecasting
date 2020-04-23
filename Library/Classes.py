'''
This contains all the classes used
'''

# Disease Classes
class Disease:
    def __init__(self, name, parameters):
        self.name = name                                                # Name of the disease
        self.parameters = parameters                                    # Parameters of the disease

class DiseaseParameters:
    def __init__(self, spreading_factor, severity, lethality, spreading_mode):
        self.spreading_factor = spreading_factor                        # Factor based on which it spreads
        self.severity = severity                                        # Severity
        self.lethality = lethality                                      # Lethality
        self.spreading_mode = spreading_mode                            # Mode of spreading

# Location Classes
class Location:
    def __init__(self, name, parameters):
        self.name = name                                                # Name of the location
        self.parameters = parameters                                    # Parameters of the location

class LocationParameters:
    def __init__(self, center_point, area_parameters, people_parameters, climate_parameters):
        self.center_point = center_point                                # Central Median point in 2D of the location
        self.area_parameters = area_parameters                          # Parameters of the area of the location
        self.people_parameters = people_parameters                      # Parameters of the people of the location
        self.climate_parameters = climate_parameters                    # Parameters of the climate of the location

# Connection Classes
# Connects 2 Locations
class Connection:
    def __init__(self, loc1, loc2, distance, connectivity_parameters, travel_rate):
        self.loc1 = loc1                                                # Location 1 of the connection
        self.loc2 = loc2                                                # Location 2 of the connection
        self.distance = distance                                        # Distance between the 2 locations
        self.connectivity_parameters = connectivity_parameters          # Parameters of the connectivity
        self.travel_rate = travel_rate                                  # TravelRate - How many people travel every day

class ConnectivityParameters:
    def __init__(self, connect_type, spreading_factor, screening_factor):
        self.connect_type = connect_type                                # Type of the connection - Water, Air, Land, etc
        self.spreading_factor = spreading_factor                        # SpreadFactor - Factor determines to how many disease spreads during travel
        self.screening_factor = screening_factor                        # ScreeningFactor - Factor determines how many people with the disease are screened and quarantined

# Climate Classes
class ClimateParameters:
    def __init__(self, season, humidity, temperature):
        self.season = season                                            # Current Season
        self.humidity = humidity                                        # Current Humidity
        self.temperature = temperature                                  # Current Temperature

# People Parameters
class PeopleParameters:
    def __init__(self, population, people_demography):
        self.population = population                                    # No of people living
        self.people_demography = people_demography                      # Splitup of the population - based on gender, access to medicines, etc

# Area Parameters
