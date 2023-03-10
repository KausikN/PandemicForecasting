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
    "default": {
        "disease": "Simulations/Test/Disease.json",
        "locations": "Simulations/Test/Locations.json",
        "connections": "Simulations/Test/Connections.json"
    },
    "temp": {
        "disease": "StreamLitGUI/TempData/Disease.json",
        "locations": "StreamLitGUI/TempData/Locations.json",
        "connections": "StreamLitGUI/TempData/Connections.json"
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
## Disease
def UI_LoadDiseaseParams(DefaultParams):
    '''
    UI - Load Disease Params
    '''
    # Init
    DefaultParams = DefaultParams.copy()
    # Name
    DefaultParams["name"] = st.text_input("Disease Name", DefaultParams["name"])
    # Disease Params (without spread mode)
    DiseaseParams_WithoutSpreadMode = {k: DefaultParams["params"][k] for k in DefaultParams["params"].keys() if k not in ["spread_mode"]}
    USERINPUT_DiseaseParams_str = st.text_area(
        "Disease Parameters", 
        json.dumps(DiseaseParams_WithoutSpreadMode, indent=8), 
        height=250
    )
    DefaultParams["params"] = json.loads(USERINPUT_DiseaseParams_str)
    # Spread Mode
    DefaultParams["params"]["spread_mode"] = {}
    cols = st.columns((1, 3))
    USERINPUT_SpreadFunc = cols[0].selectbox("Spread Function", list(SPREADMODE_FUNCS.keys()))
    DefaultParams["params"]["spread_mode"]["spread_func"] = USERINPUT_SpreadFunc
    USERINPUT_SpreadFuncParams_str = cols[1].text_area(
        "Spread Function Parameters", 
        json.dumps(SPREADMODE_FUNCS[USERINPUT_SpreadFunc]["params"], indent=8), 
        height=200
    )
    DefaultParams["params"]["spread_mode"]["spread_params"] = json.loads(USERINPUT_SpreadFuncParams_str)

    return DefaultParams

def UI_Disease():
    '''
    UI - Disease
    '''
    st.markdown("## Disease")
    USERINPUT_LoadMode = st.selectbox("Load Mode", ["Load Disease", "Edit Disease", "Load Disease JSON"])
    if USERINPUT_LoadMode == "Load Disease JSON":
        DiseaseData = st.file_uploader("Upload Disease JSON", type=["json"])
        if DiseaseData is None: DiseaseData = open(PATHS["default"]["disease"], "rb")
        DiseaseData = json.load(DiseaseData)
        DiseaseData["params"]["spread_mode"]["spread_func"] = SPREADMODE_FUNCS[DiseaseData["params"]["spread_mode"]["spread_func"]]["func"]
    elif USERINPUT_LoadMode == "Load Disease":
        DiseaseData = json.load(open(PATHS["default"]["disease"], "rb"))
    else:
        ## Load Disease Data
        if not os.path.exists(PATHS["temp"]["disease"]): DiseaseData = json.load(open(PATHS["default"]["disease"], "rb"))
        else: DiseaseData = json.load(open(PATHS["temp"]["disease"], "rb"))
        USERINPUT_Op = st.selectbox("Operation", ["Edit", "Reload"])
        if USERINPUT_Op == "Edit":
            DiseaseParams = UI_LoadDiseaseParams(DiseaseData)
            if st.button("Edit"): DiseaseData = DiseaseParams
        elif USERINPUT_Op == "Reload":
            if st.button("Reload"): DiseaseData = json.load(open(PATHS["default"]["disease"], "rb"))
        ## Save
        json.dump(DiseaseData, open(PATHS["temp"]["disease"], "w"), indent=4)
        ## Refresh
        st.button("Refresh")
        
    # Display Disease Data
    st.markdown("Final Disease Parameters")
    st.write(DiseaseData)
    # Load as funcs
    DiseaseData["params"]["spread_mode"]["spread_func"] = SPREADMODE_FUNCS[DiseaseData["params"]["spread_mode"]["spread_func"]]["func"]
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

## Locations
def UI_LoadLocationParams(DefaultParams):
    '''
    UI - Load Location Params
    '''
    # Init
    DefaultParams = DefaultParams.copy()
    # Name
    DefaultParams["name"] = st.text_input("Location Name", DefaultParams["name"])
    # Params
    cols = st.columns(2)
    ## Geographical Params
    Params_Geo = {k: DefaultParams["params"][k] for k in ["center_point", "params_area"]}
    USERINPUT_GeoParams = json.loads(cols[0].text_area(
        "Geographical Parameters", 
        json.dumps(Params_Geo, indent=4), 
        height=200
    ))
    DefaultParams["params"].update(USERINPUT_GeoParams)
    ## Population Params
    Params_Pop = DefaultParams["params"]["params_population"]["population"]
    USERINPUT_PopParams = json.loads(cols[1].text_area(
        "Population Parameters", 
        json.dumps(Params_Pop, indent=4), 
        height=200
    ))
    DefaultParams["params"]["params_population"]["population"].update(USERINPUT_PopParams)
    ### Rates
    cols = st.columns(3)
    USERINPUT_PopRateParams = {
        "birth_rate": cols[0].number_input("Birth Rate", 0.0, 1.0, DefaultParams["params"]["params_population"]["birth_rate"]),
        "death_rate": cols[1].number_input("Death Rate", 0.0, 1.0, DefaultParams["params"]["params_population"]["death_rate"]),
        "hospital_admittance_rate": cols[2].number_input("Hospital Admittance Rate", 0.0, 1.0, DefaultParams["params"]["params_population"]["hospital_admittance_rate"])
    }
    DefaultParams["params"]["params_population"].update(USERINPUT_PopRateParams)
    ## Medical Params
    cols = st.columns((1, 3))
    ### Admit Order
    DefaultParams["params"]["params_medical"]["hospitals_admit_order_func"] = cols[0].selectbox(
        "Hospital Admittance Order", list(HOSPITAL_ADMIT_ORDER_FUNCS.keys())
    )
    ### Hospitals
    Params_Hospitals = DefaultParams["params"]["params_medical"]["hospitals"]
    USERINPUT_HospitalsParams = json.loads(cols[1].text_area(
        "Hospitals Parameters", 
        json.dumps(Params_Hospitals, indent=4), 
        height=200
    ))
    DefaultParams["params"]["params_medical"]["hospitals"] = USERINPUT_HospitalsParams
    ## Other Params
    Params_Other = DefaultParams["params"]["params_other"]
    USERINPUT_OtherParams = json.loads(st.text_area(
        "Other Parameters", 
        json.dumps(Params_Other, indent=4), 
        height=25
    ))
    DefaultParams["params"]["params_other"].update(USERINPUT_OtherParams)

    return DefaultParams

def UI_Locations():
    '''
    UI - Locations
    '''
    st.markdown("## Locations")
    USERINPUT_LoadMode = st.selectbox("Load Mode", ["Load Locations", "Edit Locations", "Load Locations JSON"])
    if USERINPUT_LoadMode == "Load Locations JSON":
        LocationsData = st.file_uploader("Upload Locations JSON", type=["json"])
        if LocationsData is None: LocationsData = open(PATHS["default"]["locations"], "rb")
        LocationsData = json.load(LocationsData)
    elif USERINPUT_LoadMode == "Load Locations":
        LocationsData = json.load(open(PATHS["temp"]["locations"], "rb"))
    else:
        ## Load Locations Data
        if not os.path.exists(PATHS["temp"]["locations"]): LocationsData = json.load(open(PATHS["default"]["locations"], "rb"))
        else: LocationsData = json.load(open(PATHS["temp"]["locations"], "rb"))
        ## Old Load - Simple JSON
        # USERINPUT_Locations_str = st.text_area(
        #     "Locations", 
        #     json.dumps(LocationsData, indent=8), 
        #     height=500
        # )
        # LocationsData = json.loads(USERINPUT_Locations_str)
        ## New Load - UI
        USERINPUT_Op = st.selectbox("Operation", ["Add", "Edit", "Clear", "Reload"])
        if USERINPUT_Op == "Add":
            LocParams = UI_LoadLocationParams(LocationsData["locations"][0])
            if st.button("Add"): LocationsData["locations"].append(LocParams)
        elif USERINPUT_Op == "Edit":
            LocNames = [loc["name"] for loc in LocationsData["locations"]]
            USERINPUT_LocName = st.selectbox("Select Location", LocNames)
            USERINPUT_LocIndex = LocNames.index(USERINPUT_LocName)
            LocParams = UI_LoadLocationParams(LocationsData["locations"][USERINPUT_LocIndex])
            cols = st.columns(2)
            if cols[0].button("Edit"): LocationsData["locations"][USERINPUT_LocIndex] = LocParams
            if cols[1].button("Delete"): LocationsData["locations"].pop(USERINPUT_LocIndex)
        elif USERINPUT_Op == "Clear":
            if st.button("Clear"): LocationsData["locations"] = []
        elif USERINPUT_Op == "Reload":
            if st.button("Reload"): LocationsData = json.load(open(PATHS["default"]["locations"], "rb"))
        ## Save
        json.dump(LocationsData, open(PATHS["temp"]["locations"], "w"), indent=4)
        ## Refresh
        st.button("Refresh")
            
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

## Connections
def UI_LoadConnectionParams(DefaultParams, LocNames=[]):
    '''
    UI - Load Connection Params
    '''
    # Init
    DefaultParams = DefaultParams.copy()
    LocNames = LocNames.copy()
    # Locations
    cols = st.columns(2)
    DefaultParams["loc_1"] = cols[0].selectbox("Start Location", LocNames)
    DefaultParams["loc_2"] = cols[1].selectbox("End Location", LocNames)
    # Params
    ## Rates
    Params_Rates = {
        "travel_rate": st.number_input("Travel Rate", 0.0, 1.0, DefaultParams["travel_rate"])
    }
    DefaultParams.update(Params_Rates)
    ## Connection Type
    DefaultParams["params"]["connect_type"] = st.selectbox("Connection Type", CONNECTION_TYPES)

    return DefaultParams

def UI_Connections(LOCATIONS):
    '''
    UI - Connections
    '''
    st.markdown("## Connections")
    USERINPUT_LoadMode = st.selectbox("Load Mode", ["Load Connections", "Edit Connections", "Load Connections JSON"])
    if USERINPUT_LoadMode == "Load Connections JSON":
        ConnectionsData = st.file_uploader("Upload Connections JSON", type=["json"])
        if ConnectionsData is None: ConnectionsData = open(PATHS["default"]["connections"], "rb")
        ConnectionsData = json.load(ConnectionsData)
    elif USERINPUT_LoadMode == "Load Connections":
        ConnectionsData = json.load(open(PATHS["temp"]["connections"], "rb"))
    else:
        ## Load Connections Data
        if not os.path.exists(PATHS["temp"]["connections"]): ConnectionsData = json.load(open(PATHS["default"]["connections"], "rb"))
        else: ConnectionsData = json.load(open(PATHS["temp"]["connections"], "rb"))
        ## Old Load - Simple JSON
        # USERINPUT_Connections_str = st.text_area(
        #     "Connections", 
        #     json.dumps(ConnectionsData, indent=8), 
        #     height=500
        # )
        # ConnectionsData = json.loads(USERINPUT_Connections_str)
        ## New Load - UI
        LocNames = [loc.name for loc in LOCATIONS]
        USERINPUT_Op = st.selectbox("Operation", ["Add", "Edit", "Clear", "Reload"])
        if USERINPUT_Op == "Add":
            ConnParams = UI_LoadConnectionParams(ConnectionsData["connections"][0], LocNames)
            if st.button("Add"): ConnectionsData["connections"].append(ConnParams)
        elif USERINPUT_Op == "Edit":
            ConnNames = [conn["loc_1"] + " - " + conn["loc_2"] for conn in ConnectionsData["connections"]]
            USERINPUT_ConnName = st.selectbox("Select Connection", ConnNames)
            USERINPUT_ConnIndex = ConnNames.index(USERINPUT_ConnName)
            ConnParams = UI_LoadConnectionParams(ConnectionsData["connections"][USERINPUT_ConnIndex], LocNames)
            cols = st.columns(2)
            if cols[0].button("Edit"): ConnectionsData["connections"][USERINPUT_ConnIndex] = ConnParams
            if cols[1].button("Delete"): ConnectionsData["connections"].pop(USERINPUT_ConnIndex)
        elif USERINPUT_Op == "Clear":
            if st.button("Clear"): ConnectionsData["connections"] = []
        elif USERINPUT_Op == "Reload":
            if st.button("Reload"): ConnectionsData = json.load(open(PATHS["default"]["connections"], "rb"))
        ## Save
        json.dump(ConnectionsData, open(PATHS["temp"]["connections"], "w"), indent=4)
        ## Refresh
        st.button("Refresh")

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
    CONNECTIONS = UI_Connections(LOCATIONS)
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