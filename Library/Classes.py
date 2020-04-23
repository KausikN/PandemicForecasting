'''
This contains all the classes used
'''

# Disease Classes
class Disease:
    def __init__(self, name, parameters):
        self.name = name                                                # Name of the disease
        self.parameters = parameters                                    # Parameters of the disease

class DiseaseParameters:
    def __init__(self, spread_mode, severity, lethality, spreading_mode):
        self.spread_mode = spread_mode                                  # Mode and parameters of spreading
        self.severity = severity                                        # Severity
        self.lethality = lethality                                      # Lethality
        self.spreading_mode = spreading_mode                            # Mode of spreading

class SpreadMode:
    def __init__(self, spread_parameters, spread_function):
        self.spread_parameters = spread_parameters                      # Custom Parameters for the spread function - changes for different functions
        self.spread_function = spread_function                          # Custom function defining how disease spreads - input must be 


# Location Classes
class Location:
    def __init__(self, name, parameters):
        self.name = name                                                # Name of the location
        self.parameters = parameters                                    # Parameters of the location

class LocationParameters:
    def __init__(self, center_point, area_parameters=None, medical_parameters=None, people_parameters=None, climate_parameters=None):
        self.center_point = center_point                                # Central Median point in 2D of the location
        self.area_parameters = area_parameters                          # Parameters of the area of the location
        self.people_parameters = people_parameters                      # Parameters of the people of the location
        self.climate_parameters = climate_parameters                    # Parameters of the climate of the location
        self.medical_parameters = medical_parameters                    # Parameters of the medical situation of the location

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
    def __init__(self, connect_type, spreading_factor=None, screening_factor=None):
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
    def __init__(self, population, people_demography=None):
        self.population = population                                    # No of people living
        self.people_demography = people_demography                      # Splitup of the population - based on gender, access to medicines, etc

# Medical Parameters
class MedicalParameters:
    def __init__(self, hospitals=[]):
        self.hospitals = hospitals                                      # Hospital Data

class Hospital:
    def __init__(self, name, max_patients_treatable, recovery_factor):
        self.name = name                                                # Hospital name
        self.max_patients_treatable = max_patients_treatable            # Maximum no of patients treatable by hospital at a time
        self.recovery_factor = recovery_factor                          # Factor defines ability of a hospital to cure a patient

# Simulation Parameters
class SimulationParameters:
    # Functions
    def __init__(self, disease, locations, connection_graph, max_days=10):
        self.disease = disease                                            # Disease to simulate
        self.locations = locations                                        # Array of all locations
        self.connection_graph = connection_graph                          # Graph of connections between locations
        self.max_days = max_days                                          # Max number of days to simulate
        self.global_population = Population()                             # Global Population Init

        self.UpdatePopulationData()                                       # Update the population data

    def UpdatePopulationData(self):
        self.a = 1

# Population
class Population:
    def __init__(self):
        self.living = None
        self.dead = None
        self.affected = None
        self.unaffected = None
        self.recovered = None