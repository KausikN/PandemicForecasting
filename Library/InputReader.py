'''
Functions to read inputs from json
'''

# Imports
import json
from collections import namedtuple
import os

from Classes import *
from OtherParameterClasses import *

# Functions
def GetSimulationParameters(disease_path, locations_path, connections_path, max_days=1):
    # Parse Disease Data
    disease_data = json.load(open(disease_path, 'rb'))
    disease = ParseDiseaseData(disease_data)

    # Parse Locations Data
    locations_data = json.load(open(locations_path, 'rb'))
    locations = ParseLocationsData(locations_data)

    # Parse Connections Data
    connections_data = json.load(open(connections_path, 'rb'))
    connection_matrix = ParseConnectionsData(connections_data, locations)

    sim = SimulationParameters(disease, locations, connection_matrix, max_days)

    return sim


# Disease Data Parsing
def ParseDiseaseData(disease_data):
    # Spread Mode Parse
    # Get Spread Function, Spread Parameters, Transport Function
    spread_module, spread_parameters = ImportDiseaseCode(disease_data, "spread_function", "spread_parameters")
    transport_module, transport_parameters = ImportDiseaseCode(disease_data, "transport_function", "transport_parameters")

    spread_mode = SpreadMode(spread_parameters, spread_module.spread_function, transport_parameters, transport_module.transport_function)
    disease_parameters = DiseaseParameters(spread_mode=spread_mode, severity=disease_data["severity"], lethality=disease_data["lethality"])

    disease = Disease(disease_data["name"], disease_parameters)

    return disease

def ImportDiseaseCode(disease_data, func_name, param_name):
    module = None
    if func_name in disease_data.keys():
        path = disease_data[func_name]
        #importlib.import_module(os.path.splitext(path)[0])
        module = __import__(os.path.splitext(path)[0])

    params = None
    if param_name in disease_data.keys():
        if len(disease_data[param_name].keys()) > 0:
            params = namedtuple('DiseaseCustomParameters', disease_data[param_name].keys())(*disease_data[param_name].values())


    return module, params

# Parse Locations Data
def ParseLocationsData(locations_data):
    locations = []
    for loc_data in locations_data:
        #population = namedtuple('Population', loc_data["population"].keys())(*loc_data["population"].values())
        pop_data = loc_data["population"]
        population = Population(living=pop_data["living"], dead=pop_data["dead"], affected=pop_data["affected"], unaffected=pop_data["unaffected"], recovered=pop_data["recovered"])
        people_parameters = PeopleParameters(population, loc_data["birth_rate"], loc_data["death_rate"], loc_data["hospital_admittance_rate"])

        hospitals = []
        for hosp_data in loc_data["hospitals"]:
            #hosp = namedtuple('Struct', hosp_data.keys())(*hosp_data.values())
            hosp = Hospital(hosp_data["name"], hosp_data["max_patients_treatable"], hosp_data["treatment_factor"], hosp_data["recovery_rate"])
            hospitals.append(hosp)
        medical_parameters = MedicalParameters(hospitals)

        other_parameters = loc_data["other_parameters"]

        location_parameters = LocationParameters(loc_data["center_point"], people_parameters=people_parameters, medical_parameters=medical_parameters, other_parameters=other_parameters)
        location = Location(loc_data["name"], location_parameters)

        locations.append(location)

    return locations

# Parse Connections Data
def ParseConnectionsData(connections_data, locations):
    n_locations = len(locations)
    location_names = []
    for loc in locations:
        location_names.append(loc.name)

    connection_matrix = [[None] * n_locations] * n_locations

    for con_data in connections_data:
        i = None
        j = None
        if (not con_data["loc1"] in location_names) or (not con_data["loc2"] in location_names):
            continue

        i = location_names.index(con_data["loc1"])
        j = location_names.index(con_data["loc2"])
        if i == j:
            continue

        loc1 = locations[i]
        loc2 = locations[j]

        connectivity_parameters = ConnectivityParameters(con_data["connect_type"], spreading_factor=con_data["spreading_factor"], screening_factor=con_data["screening_factor"])
        connection = Connection(loc1, loc2, connectivity_parameters, con_data["travel_rates"])

        connection_matrix[i][j] = connection
        connection_matrix[j][i] = connection

    return connection_matrix




'''
# Driver Code
disease_path = "Disease.json"
locations_path = "Locations.json"
connections_path = "Connections.json"

max_days = 100

sim = GetSimulationParameters(disease_path, locations_path, connections_path, max_days=max_days)
'''