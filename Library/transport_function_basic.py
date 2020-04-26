'''
Transport function between 2 locations with a connection

Standard Inputs
1) Spread_Parameters - Custom Parameters for this function
2) Location_1 - 1st Location Data with all its parameters
3) Location_2 - 2nd Location Data with all its parameters
4) Connection - Connection data between the two locations and its parameters

Standard Outputs
1) Location_1 - Location 1 with the updated location data and parameters
2) Location_2 - Location 2 with the updated location data and parameters

'''

# Imports
from Classes import *

# Parameters


# Function
def transport_function(spread_parameters, location_1, location_2, con):
    pop1 = location_1.parameters.people_parameters.population
    pop2 = location_2.parameters.people_parameters.population
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

    location_1.parameters.people_parameters.population.living += popchange_loc1.living
    location_1.parameters.people_parameters.population.affected += popchange_loc1.affected
    location_1.parameters.people_parameters.population.unaffected += popchange_loc1.unaffected
    location_1.parameters.people_parameters.population.dead += popchange_loc1.dead
    location_1.parameters.people_parameters.population.recovered += popchange_loc1.recovered

    location_2.parameters.people_parameters.population.living += popchange_loc2.living
    location_2.parameters.people_parameters.population.affected += popchange_loc2.affected
    location_2.parameters.people_parameters.population.unaffected += popchange_loc2.unaffected
    location_2.parameters.people_parameters.population.dead += popchange_loc2.dead
    location_2.parameters.people_parameters.population.recovered += popchange_loc2.recovered

    return location_1, location_2