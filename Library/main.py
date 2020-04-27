'''
Main Script to run simulation
'''

# Imports
import InputReader
import Simulation

# Parameters
disease_path = "Disease.json"
locations_path = "Locations.json"
connections_path = "Connections.json"

max_days = 100
min_living = 10

progressBar = False
verbose = False


# Driver Code
sim = InputReader.GetSimulationParameters(disease_path, locations_path, connections_path, max_days=max_days)

global_history, loc_history, all_dead_day = Simulation.SimulateSpread(sim, min_living=min_living, progress=progressBar, verbose=verbose)
if all_dead_day > -1:
    print("Whole Global Population DEAD by day", all_dead_day)
Simulation.PlotPopulationHistory(global_history)
Simulation.PlotLocPopulationHistory(loc_history)