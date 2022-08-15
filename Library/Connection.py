"""
Connection
"""

# Imports


# Main Classes
# Connection Classes
class Connection:
    '''
    Class - Connection
    '''
    def __init__(self, 
        loc_1, loc_2, params, travel_rate, 
        **args
        ):
        # Location 1 of the connection
        self.loc_1 = loc_1
        # Location 2 of the connection                                  
        self.loc_2 = loc_2
        # Distance between the 2 locations
        self.distance = self.getDistance(loc_1.params.center_point, loc_2.params.center_point)
        # Parameters of the connectivity
        self.params = params
        # TravelRate - Rate of travel from 1 to 2
        self.travel_rate = travel_rate
        # Other Arguments
        self.__dict__.update(args)

    def getDistance(self, p1, p2):
        return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2) ** (0.5)

class Params_Connection:
    '''
    Class - Connection Parameters
    '''
    def __init__(self, 
        connect_type, spreading_factor, screening_factor, 
        **args
        ):
        # Type of the connection - Water, Air, Land, etc
        self.connect_type = connect_type
        # Other Arguments
        self.__dict__.update(args)

# Main Functions


# Main Vars