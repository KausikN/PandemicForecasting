"""
Simulator
"""

# Imports
import random
import numpy as np

from .Disease import *
from .Location import *
from .Connection import *

# Main Classes
class Simulator:
    '''
    Class - Simulator
    '''
    # Functions
    def __init__(self, 
        disease, locations, connections, 
        max_days=10, 
        **args
        ):
        # Disease to simulate
        self.disease = disease
        # Array of all locations
        self.locations = locations
        # Array of all connections
        self.connections = connections
        self.connection_matrix = np.ones((len(self.locations), len(self.locations))) * -1
        # Max number of days to simulate
        self.max_days = max_days
        # Global Vars
        self.globals = {}
        # Other Arguments
        self.__dict__.update(args)

        # Update connections matrix
        self.UpdateConnectionMatrix()
        # Update overall population
        self.UpdateOverallPopulation()

    def UpdateConnectionMatrix(self):
        # Create a matrix of connections
        self.connection_matrix = np.ones((len(self.locations), len(self.locations))) * -1
        location_names = [loc.name for loc in self.locations]
        # Update the matrix with the connections
        for i in range(len(self.connections)):
            connection = self.connections[i]
            ind_1 = location_names.index(connection.loc_1)
            ind_2 = location_names.index(connection.loc_2)
            self.connection_matrix[ind_1, ind_2] = i

    def UpdateOverallPopulation(self):
        # To get global population, goto every location and add up all their populations
        self.globals["population"] = Population()
        for location in self.locations:
            self.globals["population"].unaffected += location.parameters.people_parameters.population.unaffected
            self.globals["population"].recovered += location.parameters.people_parameters.population.recovered
            self.globals["population"].medicating += location.parameters.people_parameters.population.medicating
            self.globals["population"].affected += location.parameters.people_parameters.population.affected
            self.globals["population"].dead += location.parameters.people_parameters.population.dead
        self.globals["population"].updateLiving()

    def nextDay(self):
        HISTORY = {
            "locations": [],
            "connections": []
        }
        # Location Stage
        # Within each location, update the population
        for i in range(len(self.locations)):
            loc = self.locations[i]
            population_params = loc.params.params_population
            population = population_params.population

            ## Death
            new_dead_unaffected = population_params.death_rate * population.unaffected
            new_dead_recovered = population_params.death_rate * population.recovered
            new_dead_medicating = population_params.death_rate * population.medicating
            new_dead_affected = population_params.death_rate * population.affected
            population.dead += new_dead_unaffected + new_dead_recovered + new_dead_medicating + new_dead_affected
            population.unaffected -= new_dead_unaffected
            population.recovered -= new_dead_recovered
            population.medicating -= new_dead_medicating
            population.affected -= new_dead_affected
            population.updateLiving()

            ## Birth
            new_born = population_params.birth_rate * population.living
            population.unaffected += new_born
            population.updateLiving()

            ## Recovery
            ### Admitted to Hospital
            hospitals = loc.params.params_medical.hospitals
            for h in hospitals:
                new_recovered = h["hospital"].recovery_rate * h["current_patients"]
                h["current_patients"] -= new_recovered
                population.recovered += new_recovered
                population.medicating -= new_recovered
            population.updateLiving()
            ### Non-Admitted to Hospital
            new_recovered = (1.0 - disease.params.severity) * population.affected
            population.recovered += new_recovered
            population.affected -= new_recovered

            ## Disease Infection and Spread
            disease = self.disease
            hospitals = loc.params.params_medical.hospitals
            ### Deaths from Infection - Lethality
            #### Admitted to Hospital
            for h in hospitals:
                reduced_lethality = max(0.0, disease.params.lethality * h["hospital"].treatment_factor)
                new_dead_infected = reduced_lethality * h["current_patients"]
                h["current_patients"] -= new_dead_infected
                population.dead += new_dead_infected
                population.medicating -= new_dead_infected
            population.updateLiving()
            #### Non-Admitted to Hospital Population
            new_dead_affected = disease.params.lethality * population.affected
            population.dead += new_dead_affected
            population.affected -= new_dead_affected
            population.updateLiving()
            ### Spread from Disease
            loc = disease.params.spread_mode.spread_func(loc, **disease.params.spread_mode.spread_params)

            ## Admittance to Hospitals
            hospitals = loc.params.params_medical.hospitals
            admits_affected = population_params.hospital_admittance_rate * population.affected
            hospitals_admit_order = loc.params.params_medical.hospitals_admit_order_func()
            remaining_admits_affected = admits_affected
            for hi in hospitals_admit_order:
                h = hospitals[hi]
                available = h["hospital"].capacity - h["current_patients"]
                if remaining_admits_affected <= available:
                    h["current_patients"] += remaining_admits_affected
                    remaining_admits_affected = 0
                else:
                    h["current_patients"] += available
                    remaining_admits_affected -= available
            population.medicating += (admits_affected - remaining_admits_affected)
            population.affected -= (admits_affected - remaining_admits_affected)
            population.updateLiving()

            ## Update Population
            population.updateLiving()
            self.UpdateOverallPopulation()

        # Travel Stage
        # Across all connections, update the population
        ## Travel from A to B
        for i in range(len(self.connections)):
            connection = self.connections[i]
            loc_1 = connection.loc_1
            loc_2 = connection.loc_2
            population_1 = loc_1.params.params_population.population
            population_2 = loc_2.params.params_population.population
            ### Unaffected travel from A to B
            new_travel_unaffected = connection.travel_rate * population_1.unaffected
            population_1.unaffected -= new_travel_unaffected
            population_2.unaffected += new_travel_unaffected
            ### Recovered travel from A to B
            new_travel_recovered = connection.travel_rate * population_1.recovered
            population_1.recovered -= new_travel_recovered
            population_2.recovered += new_travel_recovered
            ### Affected travel from A to B
            new_travel_affected = connection.travel_rate * population_1.affected
            population_1.affected -= new_travel_affected
            population_2.affected += new_travel_affected
            ### Update Populations
            population_1.updateLiving()
            population_2.updateLiving()

        # Update Overall Population
        self.UpdateOverallPopulation()

# Main Functions


# Main Vars