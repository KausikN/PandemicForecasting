'''
Functions to simulate the spread of disease
'''

# Imports
from Classes import *
import random
import matplotlib.pyplot as plt
from tqdm import tqdm

# Main Functions
def SimulateSpread(sim, min_living=10, progress=False, verbose=True):
    sim.UpdatePopulationData()
    global_pop_history = []
    loc_pop_history = []

    # ALWAYS PUT .copy() after each recording of history

    all_dead_day = -1

    # Initial
    global_pop_history.append(sim.global_population.copy())
    for li in range(len(sim.locations)):
        loc_pop_history.append([sim.locations[li].parameters.people_parameters.population.copy()])

    if progress:
        for day in tqdm(range(sim.max_days)):
            sim.nextDay()
            global_pop_history.append(sim.global_population.copy())
            for li in range(len(sim.locations)):
                loc_pop_history[li].append(sim.locations[li].parameters.people_parameters.population.copy())
            # Check for all dead
            #print(sim.global_population.living)
            if sim.global_population.living <= min_living:
                all_dead_day = day+1
                break

    else:
        for day in range(sim.max_days):
            sim.nextDay()
            global_pop_history.append(sim.global_population.copy())
            for li in range(len(sim.locations)):
                loc_pop_history[li].append(sim.locations[li].parameters.people_parameters.population.copy())
            # Check for all dead
            #print(sim.global_population.living)
            if sim.global_population.living <= min_living:
                all_dead_day = day+1
                break

    if verbose:
        for day in range(len(global_pop_history)):
            print("Day : ", str(day))
            sim.global_population.print()
            print("\n")

    return global_pop_history, loc_pop_history, all_dead_day

# Spread Functions
class SpreadParameters_Exponential:
    def __init__(self, expval, error_magnifier):
        self.expval = expval
        self.error_magnifier = error_magnifier


def spread_function_Exponential(spread_parameters, population):
    r_precision = 2
    # Formula of spread -> new_affected = (prevaffected * (expval)) + (random_error bw [0, 1] * error_magnifier) - prev_affected
    unaffected_to_affected = 0
    recovered_to_affected = 0

    if (population.unaffected + population.recovered) == 0:
        return 0, 0

    new_affected = (population.affected * spread_parameters.expval) + spread_parameters.error_magnifier * (random.randint(-pow(10, r_precision), pow(10, r_precision))/(pow(10, r_precision))) - population.affected
    if new_affected < 0:
        new_affected = 0
    if new_affected > population.unaffected + population.recovered:
        new_affected = population.unaffected + population.recovered
    
    # Distribute affected among unaffected and recovered based on size - equally possible to be affected
    unaffected_to_affected = int(new_affected * (population.unaffected / (population.unaffected + population.recovered)))
    recovered_to_affected = int(new_affected - unaffected_to_affected)

    return unaffected_to_affected, recovered_to_affected


def transport_spread_function(spread_parameters, pop1, pop2, con):
    # Formula - travel_rate * each population
    popchange_loc1 = Population()
    popchange_loc2 = Population()

    # While travel screening_factor * affected are identified and are not allowed to travel
    traveled_affected_1 = (1 - con.connectivity_parameters.screening_factor) * pop1.affected
    popchange_loc1.affected -= con.travel_rate_1_to_2 * traveled_affected_1
    popchange_loc2.affected += con.travel_rate_1_to_2 * traveled_affected_1

    traveled_affected_2 = (1 - con.connectivity_parameters.screening_factor) * pop2.affected
    popchange_loc2.affected -= con.travel_rate_2_to_1 * traveled_affected_2
    popchange_loc1.affected += con.travel_rate_2_to_1 * traveled_affected_2

    popchange_loc1.affected = int(popchange_loc1.affected)
    popchange_loc2.affected = int(popchange_loc2.affected)

    # For other population types
    popchange_loc1.recovered = int((con.travel_rate_2_to_1 * pop2.recovered) - (con.travel_rate_1_to_2 * pop1.recovered))
    popchange_loc2.recovered = int(-1 * popchange_loc1.recovered)

    popchange_loc1.unaffected = int((con.travel_rate_2_to_1 * pop2.unaffected) - (con.travel_rate_1_to_2 * pop1.unaffected))
    popchange_loc2.unaffected = int(-1 * popchange_loc1.unaffected)

    popchange_loc1.living = int(popchange_loc1.affected + popchange_loc1.unaffected + popchange_loc1.recovered)
    popchange_loc2.living = int(popchange_loc2.affected + popchange_loc2.unaffected + popchange_loc2.recovered)

    popchange_loc1.dead = 0
    popchange_loc2.dead = 0

    return popchange_loc1, popchange_loc2

# Util Functions


# Plot Functions
def PlotPopulationHistory(history, title="Global"):
    # Plot
    history_living = []
    history_affected = []
    history_unaffected = []
    history_recovered = []
    history_dead = []
    for pop in history:
        history_living.append(pop.living)
        history_affected.append(pop.affected)
        history_unaffected.append(pop.unaffected)
        history_recovered.append(pop.recovered)
        history_dead.append(pop.dead)

    ax = plt.subplot(5, 1, 1)
    ax.title.set_text(title)
    ax.set_ylabel("Living")
    plt.plot(range(1, len(history_living)+1), history_living)

    ax = plt.subplot(5, 1, 2)
    ax.set_ylabel("Affected")
    plt.plot(range(1, len(history_affected)+1), history_affected)

    ax = plt.subplot(5, 1, 3)
    ax.set_ylabel("unaffected")
    plt.plot(range(1, len(history_unaffected)+1), history_unaffected)

    ax = plt.subplot(5, 1, 4)
    ax.set_ylabel("Recovered")
    plt.plot(range(1, len(history_recovered)+1), history_recovered)

    ax = plt.subplot(5, 1, 5)
    ax.set_ylabel("Dead")
    plt.plot(range(1, len(history_dead)+1), history_dead)

    plt.show()

def PlotLocPopulationHistory(loc_history):
    history_living = []
    history_affected = []
    history_unaffected = []
    history_recovered = []
    history_dead = []
    for i in range(len(loc_history)):
        history_living.append([])
        history_affected.append([])
        history_unaffected.append([])
        history_recovered.append([])
        history_dead.append([])
        for pop in loc_history[i]:
            history_living[i].append(pop.living)
            history_affected[i].append(pop.affected)
            history_unaffected[i].append(pop.unaffected)
            history_recovered[i].append(pop.recovered)
            history_dead[i].append(pop.dead)

    for i in range(len(loc_history)):
        ax = plt.subplot(len(loc_history)*2, 5, 1 + 5*i*2)
        ax.set_xlabel("Living")
        plt.plot(range(1, len(history_living[i])+1), history_living[i])

        ax = plt.subplot(len(loc_history)*2, 5, 2 + 5*i*2)
        ax.set_xlabel("Affected")
        plt.plot(range(1, len(history_affected[i])+1), history_affected[i])

        ax = plt.subplot(len(loc_history)*2, 5, 3 + 5*i*2)
        ax.title.set_text("Loc " + str(i+1))
        ax.set_xlabel("unaffected")
        plt.plot(range(1, len(history_unaffected[i])+1), history_unaffected[i])

        ax = plt.subplot(len(loc_history)*2, 5, 4 + 5*i*2)
        ax.set_xlabel("Recovered")
        plt.plot(range(1, len(history_recovered[i])+1), history_recovered[i])

        ax = plt.subplot(len(loc_history)*2, 5, 5 + 5*i*2)
        ax.set_xlabel("Dead")
        plt.plot(range(1, len(history_dead[i])+1), history_dead[i])
    
    plt.show()

# Driver Code
# All Params
severity = 0.95
lethality = 0.75
expval = 5
error_magnifier = 20
max_days = 100
min_living = 10
progressBar = False
verbose = False
# All Params
# Disease
# Params
spread_function = spread_function_Exponential
# Params
spread_params = SpreadParameters_Exponential(expval, error_magnifier)
spread_mode = SpreadMode(spread_params, spread_function, transport_spread_function)
diseaseParams = DiseaseParameters(spread_mode, severity, lethality)
disease = Disease("test", diseaseParams)

# Locations
# Location 1
center_point = (1, 2)
birth_rate = 0.1
death_rate = 0.025
hospital_admittance_rate = 0.75

pop1 = Population()
pop1.living = 10000
pop1.affected = 100
pop1.unaffected = pop1.living - pop1.affected
hosp_1 = Hospital("Hospital 1", 200, 0.5, 0.25)
hosp_2 = Hospital("Hospital 2", 100, 0.25, 0.5)
loc1_hospitals = [hosp_1, hosp_2]
loc1_medical_params = MedicalParameters(loc1_hospitals)
loc1_people_params = PeopleParameters(pop1, birth_rate, death_rate, hospital_admittance_rate)
loc1_params = LocationParameters(center_point, people_parameters=loc1_people_params, medical_parameters=loc1_medical_params)
loc1 = Location("loc 1", loc1_params)

# Location 2
center_point = (3, 2)
birth_rate = 0.2
death_rate = 0.1
hospital_admittance_rate = 0.35

pop2 = Population()
pop2.living = 5000
pop2.affected = 1
pop2.unaffected = pop2.living - pop2.affected
hosp_1 = Hospital("Hospital 1", 500, 0.5, 0.25)
hosp_2 = Hospital("Hospital 2", 100, 0.25, 0.5)
loc2_hospitals = [hosp_1, hosp_2]
loc2_medical_params = MedicalParameters(loc1_hospitals)
loc2_people_params = PeopleParameters(pop2, birth_rate, death_rate, hospital_admittance_rate)
loc2_params = LocationParameters(center_point, people_parameters=loc2_people_params, medical_parameters=loc2_medical_params)
loc2 = Location("loc 2", loc2_params)

# Connection 1 - 2
connect_type = "Air"
screening_factor = 0.1
travel_rates = [0.25, 0.1]
connectivity_parameters = ConnectivityParameters(connect_type, screening_factor=screening_factor)
connection_1_2 = Connection(loc1, loc2, connectivity_parameters, travel_rates)

# Simulation
# locations = [loc1, loc2]
# connection_matrix = [   
#                       [None               , connection_1_2],
#                       [connection_1_2     ,           None]
#                     ]
locations = [loc1]
connection_matrix = [   
                        [None     ,         None],
                        [None     ,         None]
                    ]
sim = SimulationParameters(disease, locations, connection_matrix, max_days)

global_history, loc_history, all_dead_day = SimulateSpread(sim, min_living=min_living, progress=progressBar, verbose=verbose)
if all_dead_day > -1:
    print("Whole Global Population DEAD by day", all_dead_day)
PlotPopulationHistory(global_history)
PlotLocPopulationHistory(loc_history)