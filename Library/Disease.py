"""
Disease
"""

# Imports
from .SpreadModes import *

# Main Classes
# Disease Classes
class Disease:
    '''
    Class - Disease
    '''
    def __init__(self, 
        name, params, 
        **args
        ):
        # Name of the disease
        self.name = name
        # Parameters of the disease
        self.params = params
        # Other Arguments
        self.__dict__.update(args)

class Params_Disease:
    '''
    Class - Disease Parameters
    '''
    def __init__(self, 
        spread_mode, severity=0.0, lethality=0.0, 
        **args
        ):
        # Mode and parameters of spreading
        self.spread_mode = spread_mode
        # Severity - 1 - recovery rate of normal affected person
        self.severity = severity
        # Lethality - % of deaths per day due to disease
        self.lethality = lethality
        # Other Arguments
        self.__dict__.update(args)

# Spread Mode Classes
class SpreadMode:
    '''
    Class - Spread Mode
    '''
    def __init__(self, 
        spread_func, spread_params,
        **args
        ):
        # Custom function defining how disease spreads
        self.spread_func = spread_func
        # Custom Parameters for the spread function - changes for different functions
        self.spread_params = spread_params
        # Other Arguments
        self.__dict__.update(args)

# Main Functions


# Main Vars