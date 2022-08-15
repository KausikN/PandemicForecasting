"""
Simulator
"""

# Imports
import random
import numpy as np
import matplotlib.pyplot as plt

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
            self.globals["population"].unaffected += location.params.params_population.population.unaffected
            self.globals["population"].recovered += location.params.params_population.population.recovered
            self.globals["population"].medicating += location.params.params_population.population.medicating
            self.globals["population"].affected += location.params.params_population.population.affected
            self.globals["population"].dead += location.params.params_population.population.dead
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
            disease = self.disease
            population_params = loc.params.params_population
            population = population_params.population
            hospitals = loc.params.params_medical.hospitals
            LOCATION_HISTORY = {
                "name": loc.name,
                "population": {
                    "start": dict(population.__dict__),
                    "end": {}
                },
                "hospitals": {
                    "start": [h["current_patients"] for h in hospitals],
                    "end": []
                },
                "stages": {
                    "death": {},
                    "birth": {},
                    "recovery": {
                        "admitted_to_hospital": {},
                        "non_admitted_to_hospital": {}
                    },
                    "disease_infection_and_spread": {
                        "deaths_from_infection": {
                            "admitted_to_hospital": {},
                            "non_admitted_to_hospital": {}
                        },
                        "spread_from_disease": {}
                    },
                    "admittance_to_hospitals": {
                        "overall": {},
                        "hospitals": []
                    }
                }
            }

            ## Death
            new_dead_unaffected = int(population_params.death_rate * population.unaffected)
            new_dead_recovered = int(population_params.death_rate * population.recovered)
            new_dead_medicating = 0
            for h in hospitals:
                new_dead_hospital = int(population_params.death_rate * h["current_patients"])
                h["current_patients"] -= new_dead_hospital
                new_dead_medicating += new_dead_hospital
            new_dead_affected = int(population_params.death_rate * population.affected)
            population.dead += new_dead_unaffected + new_dead_recovered + new_dead_medicating + new_dead_affected
            population.unaffected -= new_dead_unaffected
            population.recovered -= new_dead_recovered
            population.medicating -= new_dead_medicating
            population.affected -= new_dead_affected
            population.updateLiving()
            LOCATION_HISTORY["stages"]["death"]["unaffected"] = new_dead_unaffected
            LOCATION_HISTORY["stages"]["death"]["recovered"] = new_dead_recovered
            LOCATION_HISTORY["stages"]["death"]["medicating"] = new_dead_medicating
            LOCATION_HISTORY["stages"]["death"]["affected"] = new_dead_affected
            LOCATION_HISTORY["stages"]["death"]["population"] = dict(population.__dict__)
            LOCATION_HISTORY["stages"]["death"]["hospitals"] = [h["current_patients"] for h in hospitals]

            ## Birth
            new_born = int(population_params.birth_rate * population.living)
            population.unaffected += new_born
            population.updateLiving()
            LOCATION_HISTORY["stages"]["birth"]["living"] = new_born
            LOCATION_HISTORY["stages"]["birth"]["population"] = dict(population.__dict__)

            ## Recovery
            ### Admitted to Hospital
            hospitals = loc.params.params_medical.hospitals
            new_recovered_total = 0
            for h in hospitals:
                new_recovered = int(h["hospital"].recovery_rate * h["current_patients"])
                h["current_patients"] -= new_recovered
                population.recovered += new_recovered
                population.medicating -= new_recovered
                new_recovered_total += new_recovered
            population.updateLiving()
            LOCATION_HISTORY["stages"]["recovery"]["admitted_to_hospital"]["recovered"] = new_recovered_total
            LOCATION_HISTORY["stages"]["recovery"]["admitted_to_hospital"]["population"] = dict(population.__dict__)
            LOCATION_HISTORY["stages"]["recovery"]["admitted_to_hospital"]["hospitals"] = [h["current_patients"] for h in hospitals]
            ### Non-Admitted to Hospital
            new_recovered = int((1.0 - disease.params.severity) * population.affected)
            population.recovered += new_recovered
            population.affected -= new_recovered
            population.updateLiving()
            LOCATION_HISTORY["stages"]["recovery"]["non_admitted_to_hospital"]["recovered"] = new_recovered
            LOCATION_HISTORY["stages"]["recovery"]["non_admitted_to_hospital"]["population"] = dict(population.__dict__)

            ## Disease Infection and Spread
            disease = self.disease
            hospitals = loc.params.params_medical.hospitals
            ### Deaths from Infection - Lethality
            #### Admitted to Hospital
            new_dead_total = 0
            for h in hospitals:
                reduced_lethality = max(0.0, disease.params.lethality * h["hospital"].treatment_factor)
                new_dead_infected = int(reduced_lethality * h["current_patients"])
                h["current_patients"] -= new_dead_infected
                population.dead += new_dead_infected
                population.medicating -= new_dead_infected
                new_dead_total += new_dead_infected
            population.updateLiving()
            LOCATION_HISTORY["stages"]["disease_infection_and_spread"]["deaths_from_infection"]["admitted_to_hospital"]["dead"] = new_dead_total
            LOCATION_HISTORY["stages"]["disease_infection_and_spread"]["deaths_from_infection"]["admitted_to_hospital"]["population"] = dict(population.__dict__)
            LOCATION_HISTORY["stages"]["disease_infection_and_spread"]["deaths_from_infection"]["admitted_to_hospital"]["hospitals"] = [h["current_patients"] for h in hospitals]
            #### Non-Admitted to Hospital Population
            new_dead_affected = int(disease.params.lethality * population.affected)
            population.dead += new_dead_affected
            population.affected -= new_dead_affected
            population.updateLiving()
            LOCATION_HISTORY["stages"]["disease_infection_and_spread"]["deaths_from_infection"]["non_admitted_to_hospital"]["dead"] = new_dead_affected
            LOCATION_HISTORY["stages"]["disease_infection_and_spread"]["deaths_from_infection"]["non_admitted_to_hospital"]["population"] = dict(population.__dict__)
            ### Spread from Disease
            loc = disease.params.spread_mode.spread_func(loc, **disease.params.spread_mode.spread_params)
            population = loc.params.params_population.population
            LOCATION_HISTORY["stages"]["disease_infection_and_spread"]["spread_from_disease"]["population"] = dict(population.__dict__)

            ## Admittance to Hospitals
            hospitals = loc.params.params_medical.hospitals
            admits_affected = int(population_params.hospital_admittance_rate * population.affected)
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
            LOCATION_HISTORY["stages"]["admittance_to_hospitals"]["admits_affected"] = admits_affected
            LOCATION_HISTORY["stages"]["admittance_to_hospitals"]["admits_admitted"] = (admits_affected - remaining_admits_affected)
            LOCATION_HISTORY["stages"]["admittance_to_hospitals"]["population"] = dict(population.__dict__)
            LOCATION_HISTORY["stages"]["admittance_to_hospitals"]["hospitals"] = [h["current_patients"] for h in hospitals]

            ## Update Population
            population.updateLiving()
            self.UpdateOverallPopulation()
            ## Record Location History
            LOCATION_HISTORY["population"]["end"] = dict(population.__dict__)
            LOCATION_HISTORY["hospitals"]["end"] = [h["current_patients"] for h in hospitals]
            HISTORY["locations"].append(LOCATION_HISTORY)

        # Travel Stage
        # Across all connections, update the population
        ## Travel from A to B
        loc_names = [loc.name for loc in self.locations]
        for i in range(len(self.connections)):
            connection = self.connections[i]
            loc_1 = self.locations[loc_names.index(connection.loc_1)]
            loc_2 = self.locations[loc_names.index(connection.loc_2)]
            population_1 = loc_1.params.params_population.population
            population_2 = loc_2.params.params_population.population
            CONNECTION_HISTORY = {
                "loc_1": {       
                    "name": loc_1.name,             
                    "population": {
                        "start": dict(population_1.__dict__),
                        "end": {}
                    }
                },
                "loc_2": {
                    "name": loc_2.name,
                    "population": {
                        "start": dict(population_2.__dict__),
                        "end": {}
                    }
                },
                "travel": {
                    "unaffected": 0,
                    "recovered": 0,
                    "affected": 0
                }
            }
            ### Unaffected travel from A to B
            new_travel_unaffected = int(connection.travel_rate * population_1.unaffected)
            population_1.unaffected -= new_travel_unaffected
            population_2.unaffected += new_travel_unaffected

            ### Recovered travel from A to B
            new_travel_recovered = int(connection.travel_rate * population_1.recovered)
            population_1.recovered -= new_travel_recovered
            population_2.recovered += new_travel_recovered
            ### Affected travel from A to B
            new_travel_affected = int(connection.travel_rate * population_1.affected)
            population_1.affected -= new_travel_affected
            population_2.affected += new_travel_affected
            ### Update Populations
            population_1.updateLiving()
            population_2.updateLiving()
            ### Record Connection History
            CONNECTION_HISTORY["travel"]["unaffected"] = new_travel_unaffected
            CONNECTION_HISTORY["travel"]["recovered"] = new_travel_recovered
            CONNECTION_HISTORY["travel"]["affected"] = new_travel_affected
            CONNECTION_HISTORY["loc_1"]["population"]["end"] = dict(population_1.__dict__)
            CONNECTION_HISTORY["loc_2"]["population"]["end"] = dict(population_2.__dict__)
            HISTORY["connections"].append(CONNECTION_HISTORY)

        # Update Overall Population
        self.UpdateOverallPopulation()

        return HISTORY

# Main Functions
def VisualiseHistory_Simple(HISTORY, DISEASE, LOCATIONS, CONNECTIONS, SIMULATION_PARAMS):
    '''
    Visualise Simulation History - Simple
    '''
    # Init
    VIS_DATA = {
        "figs": {
            "Stepwise Population": {},
            "Stepwise Hospitals": {},
            "Stepwise Travel": {}
        }
    }
    # Locations
    for i in range(len(LOCATIONS)):
        # Stepwise Population
        fig = plt.figure()
        pops = [HISTORY[step]["locations"][i]["population"]["start"] for step in range(len(HISTORY))]
        pops.append(HISTORY[-1]["locations"][i]["population"]["end"])
        xs = [step for step in range(len(pops))]
        for k in pops[0].keys():
            plt.plot(xs, [p[k] for p in pops], label=k)
        plt.legend()
        plt.title(LOCATIONS[i].name + " - Stepwise Population")
        plt.xlabel("Step")
        plt.ylabel("Population")
        VIS_DATA["figs"]["Stepwise Population"][LOCATIONS[i].name] = fig
        # Stepwise Hospitals
        fig = plt.figure()
        hospitals = [HISTORY[step]["locations"][i]["hospitals"]["start"] for step in range(len(HISTORY))]
        hospitals.append(HISTORY[-1]["locations"][i]["hospitals"]["end"])
        xs = [step for step in range(len(hospitals))]
        for hi in range(len(hospitals[0])):
            hospitalObj = LOCATIONS[i].params.params_medical.hospitals[hi]["hospital"]
            label = f"{hospitalObj.name} - {hospitalObj.capacity}"
            plt.plot(xs, [h[hi] for h in hospitals], label=label)
        plt.legend()
        plt.title(LOCATIONS[i].name + " - Stepwise Hospitals")
        plt.xlabel("Step")
        plt.ylabel("Hospital Current Patients")
        VIS_DATA["figs"]["Stepwise Hospitals"][LOCATIONS[i].name] = fig
    # Connections
    for i in range(len(CONNECTIONS)):
        # Stepwise Travel
        fig = plt.figure()
        travels = [HISTORY[step]["connections"][i]["travel"] for step in range(len(HISTORY))]
        xs = [step for step in range(len(travels))]
        for k in travels[0].keys():
            plt.plot(xs, [t[k] for t in travels], label=k)
        plt.legend()
        plt.title(CONNECTIONS[i].loc_1 + " -> " + CONNECTIONS[i].loc_2 + " - Stepwise Travel")
        plt.xlabel("Step")
        plt.ylabel("Travel Count")
        VIS_DATA["figs"]["Stepwise Travel"][CONNECTIONS[i].loc_1 + " -> " + CONNECTIONS[i].loc_2] = fig

    return VIS_DATA

# Main Vars