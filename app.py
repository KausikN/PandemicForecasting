"""
Stream lit GUI for hosting PandemicForecasting
"""

# Imports
import os
import streamlit as st
import json

from PandemicForecasting import *

# Main Vars
config = json.load(open("./StreamLitGUI/UIConfig.json", "r"))

# Main Functions
def main():
    # Create Sidebar
    selected_box = st.sidebar.selectbox(
    "Choose one of the following",
        tuple(
            [config["PROJECT_NAME"]] + 
            config["PROJECT_MODES"]
        )
    )
    
    if selected_box == config["PROJECT_NAME"]:
        HomePage()
    else:
        correspondingFuncName = selected_box.replace(" ", "_").lower()
        if correspondingFuncName in globals().keys():
            globals()[correspondingFuncName]()
 

def HomePage():
    st.title(config["PROJECT_NAME"])
    st.markdown("Github Repo: " + "[" + config["PROJECT_LINK"] + "](" + config["PROJECT_LINK"] + ")")
    st.markdown(config["PROJECT_DESC"])

    # st.write(open(config["PROJECT_README"], "r").read())

#############################################################################################################################
# Repo Based Vars
PATHS = {
    "cache": "StreamLitGUI/CacheData/Cache.json",
    "temp": "StreamLitGUI/TempData/",
    "default": {
        "disease": "Simulations/Test/Disease.json",
        "locations": "Simulations/Test/Locations.json",
        "connections": "Simulations/Test/Connections.json"
    }
}

# Util Vars
CACHE = {}
SETTINGS = {
    "interactive_plots": False
}

# Util Functions
def LoadCache():
    global CACHE
    CACHE = json.load(open(PATHS["cache"], "r"))

def SaveCache():
    global CACHE
    json.dump(CACHE, open(PATHS["cache"], "w"), indent=4)

# Main Functions


# UI Functions
def UI_Disease():
    '''
    UI - Disease
    '''
    st.markdown("## Disease Parameters")
    USERINPUT_LoadMode = st.selectbox("Load Mode", ["Load Disease JSON", "Create New Disease"])
    if USERINPUT_LoadMode == "Load Disease JSON":
        DiseaseData = st.file_uploader("Upload Disease JSON", type=["json"])
        if DiseaseData is None:
            DiseaseData = open(PATHS["default"]["disease"], "rb")
        DiseaseData = json.load(DiseaseData)
        DiseaseData["params"]["spread_mode"]["spread_func"] = SPREADMODE_FUNCS[DiseaseData["params"]["spread_mode"]["spread_func"]]["func"]
    else:
        DiseaseData = json.load(open(PATHS["default"]["disease"], "rb"))
        # Name
        DiseaseData["name"] = st.text_input("Disease Name", DiseaseData["name"])
        # Disease Params (without spread mode)
        DiseaseData["params"].pop("spread_mode")
        USERINPUT_DiseaseParams_str = st.text_area(
            "Disease Parameters", 
            json.dumps(DiseaseData["params"], indent=8), 
            height=250
        )
        DiseaseData["params"] = json.loads(USERINPUT_DiseaseParams_str)
        # Spread Mode
        DiseaseData["params"]["spread_mode"] = {}
        cols = st.columns((1, 3))
        USERINPUT_SpreadFunc = cols[0].selectbox("Spread Function", list(SPREADMODE_FUNCS.keys()))
        DiseaseData["params"]["spread_mode"]["spread_func"] = SPREADMODE_FUNCS[USERINPUT_SpreadFunc]["func"]
        USERINPUT_SpreadFuncParams_str = cols[1].text_area(
            "Spread Function Parameters", 
            json.dumps(SPREADMODE_FUNCS[USERINPUT_SpreadFunc]["params"], indent=8), 
            height=200
        )
        DiseaseData["params"]["spread_mode"]["spread_params"] = json.loads(USERINPUT_SpreadFuncParams_str)
    # Display Disease Data
    st.markdown("Final Disease Parameters")
    st.write(DiseaseData)
    # Form Classes
    SPREAD_MODE = SpreadMode(**DiseaseData["params"]["spread_mode"])
    disease_params = {
        k: DiseaseData["params"][k]
            for k in DiseaseData["params"].keys()
            if k not in ["spread_mode"]
    }
    DISEASE_PARAMS = Params_Disease(SPREAD_MODE, **disease_params)
    DISEASE = Disease(DiseaseData["name"], DISEASE_PARAMS)

    return DISEASE

def UI_Locations():
    '''
    UI - Locations
    '''
    st.markdown("## Locations")
    USERINPUT_LoadMode = st.selectbox("Load Mode", ["Load Locations JSON", "Create New Locations"])
    if USERINPUT_LoadMode == "Load Locations JSON":
        LocationsData = st.file_uploader("Upload Locations JSON", type=["json"])
        if LocationsData is None:
            LocationsData = open(PATHS["default"]["locations"], "rb")
        LocationsData = json.load(LocationsData)
    else:
        LocationsData = json.load(open(PATHS["default"]["locations"], "rb"))
        USERINPUT_Locations_str = st.text_area(
            "Locations", 
            json.dumps(LocationsData, indent=8), 
            height=500
        )
        LocationsData = json.loads(USERINPUT_Locations_str)
    # Display Locations Data
    st.markdown("Final Locations")
    st.write(LocationsData)
    # Form Classes
    LOCATIONS = []
    for loc in LocationsData["locations"]:
        # Hospitals
        HOSPITALS = []
        for hospital in loc["params"]["params_medical"]["hospitals"]:
            HOSPITALS.append(Structure_Hospital(**hospital))
        # Medical Params
        medical_params = {
            k: loc["params"]["params_medical"][k]
                for k in loc["params"]["params_medical"].keys()
                if k not in ["hospitals"]
        }
        MEDICAL_PARAMS = Params_Medical(HOSPITALS, **medical_params)
        # Population
        POPULATION = Population(**loc["params"]["params_population"]["population"])
        # Population Params
        params_population = {
            k: loc["params"]["params_population"][k] 
                for k in loc["params"]["params_population"].keys()
                if k not in ["population"]
        }
        POPULATION_PARAMS = Params_Population(POPULATION, **params_population)
        # Area Params
        AreaParams_str = '{"boundary_path": "' + loc["params"]["params_area"]["boundary_path"] + '"}'
        AREA_PARAMS = Params_Area(json.loads(AreaParams_str)["boundary_path"])
        # Other Params
        OTHER_PARAMS = loc["params"]["params_other"]
        # Location Params
        LOCATION_PARAMS = Params_Location(
            loc["params"]["center_point"],
            AREA_PARAMS,
            POPULATION_PARAMS,
            MEDICAL_PARAMS,
            OTHER_PARAMS
        )
        # Location
        LOCATION = Location(loc["name"], LOCATION_PARAMS)
        LOCATIONS.append(LOCATION)

    return LOCATIONS

def UI_Connections():
    '''
    UI - Connections
    '''
    st.markdown("## Connections")
    USERINPUT_LoadMode = st.selectbox("Load Mode", ["Load Connections JSON", "Create New Connections"])
    if USERINPUT_LoadMode == "Load Connections JSON":
        ConnectionsData = st.file_uploader("Upload Connections JSON", type=["json"])
        if ConnectionsData is None:
            ConnectionsData = open(PATHS["default"]["connections"], "rb")
        ConnectionsData = json.load(ConnectionsData)
    else:
        ConnectionsData = json.load(open(PATHS["default"]["connections"], "rb"))
        USERINPUT_Connections_str = st.text_area(
            "Connections", 
            json.dumps(ConnectionsData, indent=8), 
            height=500
        )
        ConnectionsData = json.loads(USERINPUT_Connections_str)
    # Display Connections Data
    st.markdown("Final Connections")
    st.write(ConnectionsData)
    # Form Classes
    CONNECTIONS = []
    for connection in ConnectionsData["connections"]:
        # Connection Params
        CONNECTION_PARAMS = Params_Connection(**connection["params"])
        # Connection
        connection_params = {
            k: connection[k]
                for k in connection.keys()
                if k not in ["params"]
        }
        CONNECTIONS.append(Connection(params=CONNECTION_PARAMS, **connection_params))

    return CONNECTIONS

def UI_SimulatorParams():
    '''
    UI - Simulator Params
    '''
    st.markdown("## Simulator Params")
    SimulatorParams = {
        "max_days": st.number_input("N Simulation Steps", min_value=1, value=1)
    }

    return SimulatorParams

def UI_VisualiseHistory(HISTORY, DISEASE, LOCATIONS, CONNECTIONS, SIMULATOR_PARAMS):
    '''
    UI - Visualise History
    '''
    st.markdown("## Visualise History")
    VIS_DATA = VisualiseHistory_Simple(HISTORY, DISEASE, LOCATIONS, CONNECTIONS, SIMULATOR_PARAMS)
    # Check Interactive
    PLOT_FUNC = st.pyplot
    if SETTINGS["interactive_plots"]: PLOT_FUNC = st.plotly_chart
    # Plots
    st.markdown("### Plots")
    for k in VIS_DATA["figs"].keys():
        st.markdown("#### " + k)
        for fig_k in VIS_DATA["figs"][k].keys():
            st.markdown(fig_k)
            PLOT_FUNC(VIS_DATA["figs"][k][fig_k])

# Repo Based Functions
def disease_spread_simulator():
    # Title
    st.header("Disease Spread Simulator")

    # Prereq Loaders

    # Load Inputs
    DISEASE = UI_Disease()
    LOCATIONS = UI_Locations()
    CONNECTIONS = UI_Connections()
    SIMULATOR_PARAMS = UI_SimulatorParams()

    # Process Inputs
    if st.button("Simulate"):
        # Create Simulator
        SIMULATOR = Simulator(DISEASE, LOCATIONS, CONNECTIONS, **SIMULATOR_PARAMS)
        # Run Simulation
        HISTORY = []
        progressObj = st.progress(0.0)
        for i in range(SIMULATOR_PARAMS["max_days"]):
            # Run
            StepHistory = SIMULATOR.nextDay()
            HISTORY.append(StepHistory)
            # Update Progress
            progressObj.progress((i+1) / SIMULATOR_PARAMS["max_days"])
        # Display Outputs
        st.markdown("## Simulation Output")
        # st.write(HISTORY)
        UI_VisualiseHistory(HISTORY, DISEASE, LOCATIONS, CONNECTIONS, SIMULATOR_PARAMS)
    
#############################################################################################################################
# Driver Code
if __name__ == "__main__":
    # Settings
    SETTINGS["plots_interactive"] = st.sidebar.checkbox("Interactive Plots", value=False)
    # Run App
    main()