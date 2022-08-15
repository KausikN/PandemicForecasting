"""
Location
"""

# Imports
import random

# Main Classes
# Location Classes
class Location:
    '''
    Class - Location
    '''
    def __init__(self, 
        name, 
        params, 
        **args
        ):
        # Name of the location
        self.name = name
        # Parameters of the location
        self.params = params
        # Other Arguments
        self.__dict__.update(args)

class Params_Location:
    '''
    Class - Location Parameters
    '''
    def __init__(self, 
        center_point, 
        params_area, params_population, params_medical, params_other, 
        **args
        ):
        # Central Median point in 2D of the location
        self.center_point = center_point
        # Parameters of the area of the location
        self.params_area = params_area
        # Parameters of the population of the location
        self.params_population = params_population
        # Parameters of the medical situation of the location
        self.params_medical = params_medical
        # Other parameters as a dictionary of classes
        self.params_other = params_other
        # Other Arguments
        self.__dict__.update(args)

# Population Classes
class Population:
    '''
    Class - Population
    '''
    def __init__(self, 
        living=0, unaffected=0, recovered=0, medicating=0, affected=0, dead=0,
        **args
        ):
        self.living = living
        self.unaffected = unaffected
        self.recovered = recovered
        self.medicating = medicating
        self.affected = affected
        self.dead = dead

        self.__dict__.update(args)

    def print(self):
        print("Living       : ", self.living)
        print("Unaffected   : ", self.unaffected)
        print("Recovered    : ", self.recovered)
        print("Medicating   : ", self.medicating)
        print("Affected     : ", self.affected)
        print("Dead         : ", self.dead)

    def updateLiving(self):
        self.living = self.unaffected + self.recovered + self.medicating + self.affected

class Params_Population:
    '''
    Class - Population Parameters
    '''
    def __init__(self, 
        population, birth_rate, death_rate, hospital_admittance_rate, tag="", 
        **args
        ):
        # No of people living
        self.population = population
        # Birth rate - rate of births per day
        self.birth_rate = birth_rate
        # Death rate - rate of natural causes deaths per day
        self.death_rate = death_rate
        # Hostpital Admittance Rate - rate of affected people who get admitted to hospitals 
        self.hospital_admittance_rate = hospital_admittance_rate
        # Population Tag / Type
        self.tag = tag
        # Other Arguments
        self.__dict__.update(args)

# Parameters Classes
class Params_Medical:
    '''
    Class - Medical Parameters
    '''
    def __init__(self, hospitals=[], hospitals_admit_order_func="random", **args):
        '''
        Medical Parameters
        
        Args:
            - hospitals
                - type: list of Hospital objects
                - description: List of hospitals in the location
            - hospitals_admit_order_func
                - type: string
                - description: Function to determine the order in which hospitals are visited by admittants
                - options: "simple", "random", "ascending_availability", "descending_availability"
        '''
        # Function Map
        self.hospitals_admit_order_funcs = {
            "simple": self.HospitalsAdmitOrder_Simple,
            "random": self.HospitalsAdmitOrder_Random,
            "ascending_availability": self.HospitalsAdmitOrder_AscendingAvailability,
            "descending_availability": self.HospitalsAdmitOrder_DescendingAvailability
        }
        # Hospital Data
        self.hospitals = [{
            "hospital": h,
            "current_patients": 0
        } for h in hospitals]
        self.hospitals_admit_order_func = self.hospitals_admit_order_funcs[hospitals_admit_order_func]

        # Other Arguments
        self.__dict__.update(args)

    def HospitalsAdmitOrder_Simple(self):
        return list(range(len(self.hospitals)))

    def HospitalsAdmitOrder_Random(self):
        order = list(range(len(self.hospitals)))
        random.shuffle(order)
        return order

    def HospitalsAdmitOrder_AscendingAvailability(self):
        return sorted(
            range(len(self.hospitals)), 
            key=lambda k: 
                (self.hospitals[k]["hospital"].capacity - self.hospitals[k]["current_patients"])
        )

    def HospitalsAdmitOrder_DescendingAvailability(self):
        return sorted(
            range(len(self.hospitals)), 
            key=lambda k: 
                (self.hospitals[k]["hospital"].capacity - self.hospitals[k]["current_patients"]),
            reverse=True
        )

class Params_Area:
    '''
    Class - Area Parameters
    '''
    def __init__(self, boundary_path=[], **args):
        # Boundary Path Points
        self.boundary_path = boundary_path
        # Other Arguments
        self.__dict__.update(args)

# Structures Classes
class Structure_Hospital:
    '''
    Class - Hospital
    '''
    def __init__(self, 
        name, capacity, 
        treatment_factor, spread_prevention_factor, 
        recovery_rate, 
        **args
        ):
        # Hospital name
        self.name = name
        # Maximum no of patients treatable by hospital at a time
        self.capacity = capacity
        # Factor defines the multiplier to lethality for a admitted patient
        self.treatment_factor = treatment_factor
        # Factor defines rate of a hospital to cure patients
        self.recovery_rate = recovery_rate
        # Other Arguments
        self.__dict__.update(args)

# Main Functions


# Main Vars