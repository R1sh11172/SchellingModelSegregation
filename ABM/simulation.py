import numpy as np
import random
import pandas as pd
import networkx as nx
from employee import Employee
from space import Space
from social_graph import create_teams, create_friendships, generate_team_structure, generate_friendships

class InteractionHandler:
    def __init__(self, team_graph, friendship_graph):
        self.team_graph = team_graph
        self.friendship_graph = friendship_graph

    # Handles interactions between employees in the same space
    def handle_interactions(self, spaces, timestep):
        for space in spaces:
            occupants = space.occupants
            for i in range(len(occupants)):
                for j in range(i + 1, len(occupants)):
                    occupants[i].interact(occupants[j], self.team_graph, self.friendship_graph, timestep)

import pandas as pd

class MetricsHandler:
    def __init__(self, emps, spaces):
        self.emps = emps
        self.spaces = spaces
        self.interactions_df = pd.DataFrame(columns=["time_step", "eid1", "eid2"])
        self.movements_df = pd.DataFrame(columns=["time_step", "eid", "space"])
        self.information_dissemination = pd.DataFrame()
        self.spatial_usage = pd.DataFrame()
        self.spatial_usage_by_type = pd.DataFrame()
        self.centrality_metrics = pd.DataFrame(columns=["eid", "hierarchy_level", "degree_centrality", "closeness_centrality", "betweenness_centrality", "pagerank"])

    # Records employee interactions
    def record_interaction(self, t, emp_a, emp_b):
        self.interactions_df = self.interactions_df.append({"time_step": t, "eid1": emp_a, "eid2": emp_b}, ignore_index=True)

    # Records employee movements
    def record_movement(self, t, emp, space):
        self.movements_df = self.movements_df.append({"time_step": t, "eid": emp, "space": space}, ignore_index=True)

    # Calculates metrics related to information dissemination
    def calculate_metrics(self):
        informed_count = sum(1 for e in self.emps if "Important Information" in e.info)
        informed_percentage = (informed_count / len(self.emps)) * 100
        self.information_dissemination = self.information_dissemination.append({
            "time_step": len(self.information_dissemination), 
            "informed_count": informed_count, 
            "informed_percentage": informed_percentage}, ignore_index=True)
        return informed_count, informed_percentage

    def calculate_centrality_metrics(self):
        # Create a graph from interactions_df
        G = nx.from_pandas_edgelist(self.interactions_df, "eid1", "eid2")

        # Calculate centrality metrics for each employee
        degree_centrality = nx.degree_centrality(G)
        closeness_centrality = nx.closeness_centrality(G)
        betweenness_centrality = nx.betweenness_centrality(G)
        pagerank = nx.pagerank(G)

        for emp in self.emps:
            eid = emp.eid
            hierarchy_level = emp.hierarchy_level

            self.centrality_metrics = self.centrality_metrics.append({
                "eid": eid,
                "hierarchy_level": hierarchy_level,
                "degree_centrality": degree_centrality.get(eid, 0),
                "closeness_centrality": closeness_centrality.get(eid, 0),
                "betweenness_centrality": betweenness_centrality.get(eid, 0),
                "pagerank": pagerank.get(eid, 0)
            }, ignore_index=True)

    # Calculate spatial usage
    def calculate_spatial_usage(self):
        space_usage = {}
        space_usage_by_type = {}
        for space in self.spaces:
            space_usage[space.sid] = len(space.occupants)
            if space.stype not in space_usage_by_type:
                space_usage_by_type[space.stype] = 0
            space_usage_by_type[space.stype] += len(space.occupants)
        self.spatial_usage = self.spatial_usage.append(space_usage, ignore_index=True)
        self.spatial_usage_by_type = self.spatial_usage_by_type.append(space_usage_by_type, ignore_index=True)

    # Prints the current state of the simulation
    def print_simulation_state(self, t, informed_count, informed_percentage):
        print(f"Time step {t + 1}")
        print(f"Informed employees: {informed_count}/{len(self.emps)} ({informed_percentage:.2f}%)")

        for space in self.spaces:
            print(f"Space {space.sid} ({space.stype}): {[e.eid for e in space.occupants]}")
        print(f"Information spread: {[e.eid for e in self.emps if 'Important Information' in e.info]}")
        print()


# Initializes the simulation with the given parameters
def initialize_simulation(num_employees, num_teams, min_team_size, num_friendships, num_spaces, 
                          space_types, space_capacities, hierarchy_levels, hierarchy_adjustment_factor):
    
    ## initialize employees and teams, each employee is (eid, position, team, hierarchy_level, hierarchy_adjustment_factor)
    team_structure = generate_team_structure(num_employees, num_teams, min_team_size)
    emps = [Employee(i, "Employee", None, random.randint(1, hierarchy_levels), hierarchy_adjustment_factor) for i in range(1, num_employees + 1)]
    team_graph = create_teams(emps, team_structure)

    ## initialize friendships
    friendships = generate_friendships(emps, num_friendships)
    friendship_graph = create_friendships(emps, friendships)

    ## initialize spaces
    spaces = [Space(i, space_types[i-1], space_capacities[i-1], (random.uniform(0, 100), random.uniform(0, 100))) for i in range(1, num_spaces + 1)]

    return emps, spaces, team_graph, friendship_graph

# Runs the simulation for the given number of time steps
def run_simulation(emps, spaces, time_steps, initial_info_holder, team_graph, friendship_graph, hierarchy_threshold, print=False):
    emps[initial_info_holder - 1].info.add("Important Information") ## add initial information

    ## initialize handlers
    interaction_handler = InteractionHandler(team_graph, friendship_graph)
    metrics_handler = MetricsHandler(emps, spaces)

    ## add metricshandler to employees
    for emp in emps:
        emp.metrics_handler = metrics_handler

    ## run simulation
    for t in range(time_steps):
        # Update employee locations
        for emp in emps:
            cur_space = emp.loc
            if cur_space is not None:
                cur_space.remove_occupant(emp)

            emp.move(spaces, threshold=hierarchy_threshold, timestep=t)
            new_space = emp.loc
            new_space.add_occupant(emp)

        # Simulate interactions between employees in the same space
        interaction_handler.handle_interactions(spaces, timestep=t)

        # Calculate and print metrics
        informed_count, informed_percentage = metrics_handler.calculate_metrics()
        metrics_handler.calculate_spatial_usage()
        if print:
            metrics_handler.print_simulation_state(t, informed_count, informed_percentage)
    return metrics_handler









