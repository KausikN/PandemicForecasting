'''
Spread Function for the disease

Standard Inputs
1) Spread_Parameters - Custom Parameters for this function
2) Location - Location Data with all its parameters

Standard Outputs
1) Location - Location with the updated location data and parameters

'''

# Imports
import random

# Parameters
class SpreadParameters:
    def __init__(self, expval, error_magnifier):
        self.expval = expval
        self.error_magnifier = error_magnifier

# Function
def spread_function(spread_parameters, location):
    r_precision = 2
    population = location.parameters.people_parameters.population
    # Formula of spread -> new_affected = (prevaffected * (expval)) + (random_error bw [0, 1] * error_magnifier) - prev_affected
    unaffected_to_affected = 0
    recovered_to_affected = 0

    if (population.unaffected + population.recovered) == 0:
        unaffected_to_affected = 0
        recovered_to_affected = 0

        location.parameters.people_parameters.population.affected += int(unaffected_to_affected + recovered_to_affected)
        location.parameters.people_parameters.population.unaffected -= int(unaffected_to_affected)
        location.parameters.people_parameters.population.recovered -= int(recovered_to_affected)

        return location

    new_affected = (population.affected * spread_parameters.expval) + spread_parameters.error_magnifier * (random.randint(-pow(10, r_precision), pow(10, r_precision))/(pow(10, r_precision))) - population.affected
    if new_affected < 0:
        new_affected = 0
    if new_affected > population.unaffected + population.recovered:
        new_affected = population.unaffected + population.recovered
    
    # Distribute affected among unaffected and recovered based on size - equally possible to be affected
    unaffected_to_affected = int(new_affected * (population.unaffected / (population.unaffected + population.recovered)))
    recovered_to_affected = int(new_affected - unaffected_to_affected)

    location.parameters.people_parameters.population.affected += int(unaffected_to_affected + recovered_to_affected)
    location.parameters.people_parameters.population.unaffected -= int(unaffected_to_affected)
    location.parameters.people_parameters.population.recovered -= int(recovered_to_affected)

    return location