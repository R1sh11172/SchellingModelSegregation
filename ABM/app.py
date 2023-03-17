import streamlit as st
import numpy as np
from employee import Employee
from space import Space
from social_graph import create_teams, create_friendships, generate_team_structure, generate_friendships
from simulation import run_simulation, initialize_simulation

# Display title and introduction
st.title("Open-Plan Office Space Simulation")
st.write("This app simulates the impact of formal and informal social structures on spatial usage and information dissemination within an open-plan office space.")

# Set up sidebar for input parameters
st.sidebar.header("Simulation Parameters")
num_employees = st.sidebar.number_input("Number of employees", min_value=1, value=100)
num_teams = st.sidebar.number_input("Number of teams", min_value=1, value=10)
min_team_size = st.sidebar.number_input("Minimum team size", min_value=1, value=8)
num_friendships = st.sidebar.number_input("Number of friendships", min_value=1, value=5)
num_workstations = st.sidebar.number_input("Number of workstations", min_value=1, value=30)
num_meeting_rooms = st.sidebar.number_input("Number of meeting rooms", min_value=1, value=10)
num_break_areas = st.sidebar.number_input("Number of break areas", min_value=1, value=5)
time_steps = st.sidebar.number_input("Number of time steps", min_value=1, value=10)

# Set up button to run the simulation
run_button = st.sidebar.button("Run Simulation")

# Function to display the simulation state at each time step
def display_simulation_state(emps, spaces, step):
    st.subheader(f"Time step {step}")

    for space in spaces:
        st.write(f"Space {space.sid} ({space.stype}): {[e.eid for e in space.occupants]}")
    st.write(f"Information spread: {[e.eid for e in emps if 'Important Information' in e.info]}")
    st.write("")

if run_button:
    emps, spaces, team_graph, friendship_graph = initialize_simulation(num_employees, num_teams, min_team_size,
                                                                       num_friendships, num_workstations, num_meeting_rooms, num_break_areas)

    initial_info_holder = 1
    emps[initial_info_holder - 1].info.add("Important Information")

    for t in range(time_steps):
        # Update employee locations
        for emp in emps:
            cur_space = emp.loc
            if cur_space is not None:
                cur_space.remove_occupant(emp)

            emp.move(spaces)
            new_space = emp.loc
            new_space.add_occupant(emp)

        # Simulate interactions between employees in the same space
        for space in spaces:
            occupants = space.occupants
            for i in range(len(occupants)):
                for j in range(i + 1, len(occupants)):
                    occupants[i].interact(occupants[j], team_graph, friendship_graph)

        # Display the current state of the office and information spread
        display_simulation_state(emps, spaces, t+1)
