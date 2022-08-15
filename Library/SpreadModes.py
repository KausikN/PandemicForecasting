"""
Disease Spread Modes
"""

# Imports


# Main Classes


# Main Functions
def SpreadMode_Simple(
    location, 
    spread_rates={
        "unaffected": 0.2,
        "recovered": 0.05
    }, 
    spread_func="linear",
    **params
    ):
    '''
    SpreadMode - Simple Formulaic Spread

    Args:
        - location
            - type: Location object
            - description: Location to spread disease to
        - spread_rates
            - type: dict
            - description: Dictionary of disease spread rates
        - spread_func
            - type: str
            - description: Spread function to use
            - options: "linear"
    '''
    # Init
    population = location.params.params_population.population
    spread_funcs = {
        "linear": lambda p, r: p * r
    }
    # Spread
    ## Unaffected
    new_affected_unaffected = spread_funcs[spread_func](population.unaffected, spread_rates["unaffected"])
    new_affected_unaffected = max(0, min(population.unaffected, int(new_affected_unaffected)))
    population.unaffected -= new_affected_unaffected
    population.affected += new_affected_unaffected
    ## Recovered
    new_affected_recovered = spread_funcs[spread_func](population.recovered, spread_rates["recovered"])
    new_affected_recovered = max(0, min(population.recovered, int(new_affected_recovered)))
    population.recovered -= new_affected_recovered
    population.affected += new_affected_recovered
    # Update Population
    population.updateLiving()

    return location

# Main Vars
SPREADMODE_FUNCS = {
    "simple": {
        "func": SpreadMode_Simple,
        "params": {
            "spread_rates": {
                "unaffected": 0.2,
                "recovered": 0.05
            },
            "spread_func": "linear"
        }
    }
}