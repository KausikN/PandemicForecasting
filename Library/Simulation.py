'''
Functions to simulate the spread of disease
'''

# Imports
from Classes import *
import random
import matplotlib.pyplot as plt
from tqdm import tqdm

# Main Functions
def SimulateSpread(sim, progress=False, verbose=True):
    sim.UpdatePopulationData()
    global_pop_history = []
    global_pop_history.append(sim.global_population)

    if progress:
        for day in tqdm(range(sim.max_days)):
            sim.nextDay()
            global_pop_history.append(sim.global_population)
    else:
        for day in range(sim.max_days):
            sim.nextDay()
            global_pop_history.append(sim.global_population)

    if verbose:
        for day in range(len(global_pop_history)):
            print("Day : ", str(day))
            sim.global_population.print()
            print("\n")

    return global_pop_history

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



# Driver Code
# Disease
# Params
severity = 0.1
lethality = 0.1
expval = 2
error_magnifier = 2
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

pop1 = Population()
pop1.living = 100
pop1.affected = 1
pop1.unaffected = pop1.living - pop1.affected
loc1_people_params = PeopleParameters(pop1, birth_rate, death_rate)
loc1_params = LocationParameters(center_point, people_parameters=loc1_people_params)
loc1 = Location("loc 1", loc1_params)

# Location 2
center_point = (3, 2)
birth_rate = 0.2
death_rate = 0.1

pop2 = Population()
pop2.living = 50
pop2.affected = 1
pop2.unaffected = pop2.living - pop2.affected
loc2_people_params = PeopleParameters(pop2, birth_rate, death_rate)
loc2_params = LocationParameters(center_point, people_parameters=loc2_people_params)
loc2 = Location("loc 2", loc2_params)

# Connection 1 - 2
connect_type = "Air"
screening_factor = 0.1
travel_rates = [0.2, 0.35]
connectivity_parameters = ConnectivityParameters(connect_type, screening_factor=screening_factor)
connection_1_2 = Connection(loc1, loc2, connectivity_parameters, travel_rates)

# Simulation
max_days = 100
progressBar = True
verbose = False
locations = [loc1, loc2]
connection_matrix = [   [None               , connection_1_2],
                        [connection_1_2     ,           None]
                    ]
sim = SimulationParameters(disease, locations, connection_matrix, max_days)

history = SimulateSpread(sim, progress=progressBar, verbose=verbose)
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
ax.title.set_text("Living")
plt.plot(range(1, len(history_living)+1), history_living)

ax = plt.subplot(5, 1, 2)
ax.title.set_text("Affected")
plt.plot(range(1, len(history_affected)+1), history_affected)

ax = plt.subplot(5, 1, 3)
ax.title.set_text("unaffected")
plt.plot(range(1, len(history_unaffected)+1), history_unaffected)

ax = plt.subplot(5, 1, 4)
ax.title.set_text("Recovered")
plt.plot(range(1, len(history_recovered)+1), history_recovered)

ax = plt.subplot(5, 1, 5)
ax.title.set_text("Dead")
plt.plot(range(1, len(history_dead)+1), history_dead)

plt.show()