'''
This contains all the classes used
'''

# Imports
import random

# Disease Classes
class Disease:
    def __init__(self, name, parameters=None):
        self.name = name                                                # Name of the disease
        self.parameters = parameters                                    # Parameters of the disease

class DiseaseParameters:
    def __init__(self, spread_mode=None, severity=0.0, lethality=0.0):
        self.spread_mode = spread_mode                                  # Mode and parameters of spreading
        self.severity = severity                                        # Severity - 1 - recovery rate of normal affected person
        self.lethality = lethality                                      # Lethality - % of deaths per day due to disease

class SpreadMode:
    def __init__(self, spread_parameters, spread_function, transport_parameters, transport_function):
        self.spread_parameters = spread_parameters                      # Custom Parameters for the spread function - changes for different functions
        self.spread_function = spread_function                          # Custom function defining how disease spreads
        self.transport_parameters = transport_parameters                # Custom Parameters for the transport function - changes for different functions
        self.transport_function = transport_function                    # Custom function defining how disease spreads via transport
        
# Location Classes
class Location:
    def __init__(self, name, parameters):
        self.name = name                                                # Name of the location
        self.parameters = parameters                                    # Parameters of the location

    def copy(self):
        return Location(self.name, self.parameters)

class LocationParameters:
    def __init__(self, center_point, area_parameters=None, people_parameters=None, medical_parameters=None, other_parameters=None):
        self.center_point = center_point                                # Central Median point in 2D of the location
        self.area_parameters = area_parameters                          # Parameters of the area of the location
        self.people_parameters = people_parameters                      # Parameters of the people of the location
        self.medical_parameters = medical_parameters                    # Parameters of the medical situation of the location
        self.other_parameters = other_parameters                        # Other parameters as a dictionary of classes

# Basic Parameters
# People Parameters
class PeopleParameters:
    def __init__(self, population, birth_rate, death_rate, hospital_admittance_rate, people_demography=None):
        self.population = population                                    # No of people living
        self.birth_rate = birth_rate                                    # Birth rate - rate of births per day
        self.death_rate = death_rate                                    # Death rate - rate of natural causes deaths per day
        self.hospital_admittance_rate = hospital_admittance_rate        # Hostpital Admittance Rate - rate of affected people who get admitted to hospitals 
        self.people_demography = people_demography                      # Splitup of the population - based on gender, access to medicines, etc

# Medical Parameters
class MedicalParameters:
    def __init__(self, hospitals=[]):
        self.hospitals = hospitals                                      # Hospital Data

# Connection Classes
# Connects 2 Locations
class Connection:
    def __init__(self, loc1, loc2, connectivity_parameters, travel_rates):
        self.loc1 = loc1                                                # Location 1 of the connection
        self.loc2 = loc2                                                # Location 2 of the connection
        self.distance = self.getDistance(loc1.parameters.center_point, loc2.parameters.center_point) # Distance between the 2 locations
        self.connectivity_parameters = connectivity_parameters          # Parameters of the connectivity
        self.travel_rate_1_to_2 = travel_rates[0]                       # TravelRate - How many people travel every day from 1 to 2
        self.travel_rate_2_to_1 = travel_rates[1]                       # TravelRate - How many people travel every day from 2 to 1

    def getDistance(self, p1, p2):
        return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2) ** (0.5)

class ConnectivityParameters:
    def __init__(self, connect_type, spreading_factor=None, screening_factor=None):
        self.connect_type = connect_type                                # Type of the connection - Water, Air, Land, etc
        self.spreading_factor = spreading_factor                        # SpreadFactor - Factor determines to how many disease spreads during travel
        self.screening_factor = screening_factor                        # ScreeningFactor - Factor determines how many people with the disease are screened and quarantined

# Simulation Parameters
class SimulationParameters:
    # Functions
    def __init__(self, disease, locations, connection_matrix, max_days=10):
        self.disease = disease                                            # Disease to simulate
        self.locations = locations                                        # Array of all locations
        self.connection_matrix = connection_matrix                        # Matrix of connections between locations
        self.max_days = max_days                                          # Max number of days to simulate
        self.global_population = Population()                             # Global Population Init

        self.UpdatePopulationData()                                       # Update the population data

    def UpdatePopulationData(self):
        # To get global population, goto every location and add up all their populations
        self.global_population = Population()
        for location in self.locations:
            self.global_population.dead += location.parameters.people_parameters.population.dead
            self.global_population.affected += location.parameters.people_parameters.population.affected
            self.global_population.unaffected += location.parameters.people_parameters.population.unaffected
            self.global_population.recovered += location.parameters.people_parameters.population.recovered
            # self.global_population.print()
            # print("\n")
        self.global_population.living = self.global_population.affected + self.global_population.unaffected + self.global_population.recovered

    def nextDay(self):
        # First update populations due to birth and death rates
        for i in range(len(self.locations)):
            ppl = self.locations[i].parameters.people_parameters
            new_births = int(ppl.population.living * ppl.birth_rate)
            new_deaths = int(ppl.population.living * ppl.death_rate)
            affected_change = -1 * new_deaths * (ppl.population.affected / ppl.population.living) # Assuming no new born can be affected
            unaffected_change = new_births - new_deaths * (ppl.population.unaffected / ppl.population.living)
            recovered_change = -1 * new_deaths * (ppl.population.recovered / ppl.population.living) # Assuming no new born can immediately be recovered
            if ((ppl.population.living + new_births - new_deaths) < 0): # If all dead
                self.locations[i].parameters.people_parameters.population.dead += ppl.population.living
                self.locations[i].parameters.people_parameters.population.living = 0
                self.locations[i].parameters.people_parameters.population.affected = 0
                self.locations[i].parameters.people_parameters.population.unaffected = 0
                self.locations[i].parameters.people_parameters.population.recovered = 0
            else:
                self.locations[i].parameters.people_parameters.population.dead += int(new_deaths)
                self.locations[i].parameters.people_parameters.population.unaffected += int(unaffected_change)
                self.locations[i].parameters.people_parameters.population.affected += int(affected_change)
                self.locations[i].parameters.people_parameters.population.recovered += int(recovered_change)
                self.locations[i].parameters.people_parameters.population.living = self.locations[i].parameters.people_parameters.population.unaffected + self.locations[i].parameters.people_parameters.population.affected + self.locations[i].parameters.people_parameters.population.recovered

        # Next Address Spread Within the Location
        if not self.disease.parameters.spread_mode.spread_function == None:
            for i in range(len(self.locations)):
                # print("Spread")
                # print(i)
                # Using Spread Function get change from unaffected to affected and from recovered to affected
                self.locations[i] = self.disease.parameters.spread_mode.spread_function(
                    self.disease.parameters.spread_mode.spread_parameters,
                    self.locations[i])
                
                
        
        # Calculate how many people leave and come into via transport using transport spread function of disease
        if not self.disease.parameters.spread_mode.transport_function == None:
            for i in range(len(self.locations)):
                for j in range(i+1, len(self.locations)):
                    con = self.connection_matrix[i][j]
                    con.loc1 = self.locations[i]
                    con.loc2 = self.locations[j]
                    if not con == None:
                        # print("Trans:")
                        # print(i, j)
                        self.locations[i], self.locations[j] = self.disease.parameters.spread_mode.transport_function(
                            self.disease.parameters.spread_mode.spread_parameters,
                            self.locations[i],
                            self.locations[j],
                            con)
                        
                    
        # Calculate Recovered and admitted to hospitals
        for i in range(len(self.locations)):
            # If no hospitals
            if self.locations[i].parameters.medical_parameters == None:
                # Calculate deaths
                death_count = int(self.disease.parameters.lethality * self.locations[i].parameters.people_parameters.population.affected)
                self.locations[i].parameters.people_parameters.population.affected -= int(death_count)
                self.locations[i].parameters.people_parameters.population.living -= int(death_count)
                self.locations[i].parameters.people_parameters.population.dead += int(death_count)

                # Calculate recovered
                recovery_count = int((1 - self.disease.parameters.severity) * self.locations[i].parameters.people_parameters.population.affected)
                self.locations[i].parameters.people_parameters.population.affected -= int(recovery_count)
                self.locations[i].parameters.people_parameters.population.recovered += int(recovery_count)

            # If hospitals are there
            else:
                # First calculate how many deaths
                # For admitted patients lethality = actual lethality * treatment_factor
                admitted = 0
                death_count = 0
                for hosp_index in range(len(self.locations[i].parameters.medical_parameters.hospitals)):
                    admitted += self.locations[i].parameters.medical_parameters.hospitals[hosp_index].current_patients
                    new_deaths = int(self.locations[i].parameters.medical_parameters.hospitals[hosp_index].current_patients * self.disease.parameters.lethality * self.locations[i].parameters.medical_parameters.hospitals[hosp_index].treatment_factor)
                    if self.locations[i].parameters.medical_parameters.hospitals[hosp_index].current_patients - new_deaths < 0:
                        new_deaths = self.locations[i].parameters.medical_parameters.hospitals[hosp_index].current_patients
                    self.locations[i].parameters.medical_parameters.hospitals[hosp_index].current_patients -= new_deaths
                    death_count += new_deaths
                #print("i:", self.locations[i].parameters.people_parameters.population.affected, admitted)
                unadmitted = self.locations[i].parameters.people_parameters.population.affected - admitted
                # For not admitted patients lethality = actual lethality
                new_deaths = int(self.disease.parameters.lethality * unadmitted)
                #print("d:", unadmitted, new_deaths)
                unadmitted -= new_deaths
                death_count += new_deaths
                self.locations[i].parameters.people_parameters.population.affected -= int(death_count)
                self.locations[i].parameters.people_parameters.population.living -= int(death_count)
                self.locations[i].parameters.people_parameters.population.dead += int(death_count)

                # Calculate recovered
                recovery_count = 0
                for hosp_index in range(len(self.locations[i].parameters.medical_parameters.hospitals)):
                    new_recovery = int(self.locations[i].parameters.medical_parameters.hospitals[hosp_index].current_patients * self.locations[i].parameters.medical_parameters.hospitals[hosp_index].recovery_rate)
                    if self.locations[i].parameters.medical_parameters.hospitals[hosp_index].current_patients - new_recovery < 0:
                        new_recovery = self.locations[i].parameters.medical_parameters.hospitals[hosp_index].current_patients
                    self.locations[i].parameters.medical_parameters.hospitals[hosp_index].current_patients -= new_recovery
                    recovery_count += new_recovery

                new_recovery = int((1 - self.disease.parameters.severity) * unadmitted)
                #print("r:", unadmitted, new_recovery)
                unadmitted -= new_recovery
                recovery_count += new_recovery
                self.locations[i].parameters.people_parameters.population.affected -= int(recovery_count)
                self.locations[i].parameters.people_parameters.population.recovered += int(recovery_count)

                # Calculate Admittance to hospitals
                ppl_to_admit = int(self.locations[i].parameters.people_parameters.hospital_admittance_rate * unadmitted)
                for hosp_index in range(len(self.locations[i].parameters.medical_parameters.hospitals)):
                    hosp = self.locations[i].parameters.medical_parameters.hospitals[hosp_index]
                    adm = random.randint(0, ppl_to_admit)
                    if adm > hosp.max_patients_treatable - hosp.current_patients:
                        adm = hosp.max_patients_treatable - hosp.current_patients
                    self.locations[i].parameters.medical_parameters.hospitals[hosp_index].current_patients += adm
                    ppl_to_admit -= adm
                    if ppl_to_admit == 0:
                        break



        for i in range(len(self.locations)):
            self.locations[i].parameters.people_parameters.population = self.convPop2Int(self.locations[i].parameters.people_parameters.population)

        self.UpdatePopulationData()
    
    def convPop2Int(self, pop):
        pop.dead = int(pop.dead)
        pop.affected = int(pop.affected)
        pop.unaffected = int(pop.unaffected)
        pop.recovered = int(pop.recovered)
        pop.living = int(pop.affected + pop.unaffected + pop.recovered)
        return pop


# Util Classes
# Population
class Population:
    def __init__(self, living=0, dead=0, affected=0, unaffected=0, recovered=0):
        self.living = living
        self.dead = dead
        self.affected = affected
        self.unaffected = unaffected
        self.recovered = recovered

    def print(self):
        print("Living       : ", self.living)
        print("Dead         : ", self.dead)
        print("Affected     : ", self.affected)
        print("Unaffected   : ", self.unaffected)
        print("Recovered    : ", self.recovered)

    def copy(self):
        pop = Population()
        pop.living = self.living
        pop.dead = self.dead
        pop.affected = self.affected
        pop.unaffected = self.unaffected
        pop.recovered = self.recovered
        return pop

# Hospital
class Hospital:
    def __init__(self, name, max_patients_treatable, treatment_factor, recovery_rate):
        self.name = name                                                # Hospital name
        self.current_patients = 0                                       # Current patients in hospital
        self.max_patients_treatable = max_patients_treatable            # Maximum no of patients treatable by hospital at a time
        self.treatment_factor = treatment_factor                        # Factor defines the reduction in lethality for a admitted patient
        self.recovery_rate = recovery_rate                              # Factor defines rate of a hospital to cure patients
