import numpy as np
import networkx as nx
import itertools
import random
from employee import Employee

def create_teams(employees, team_structure):
    team_graph = nx.Graph()

    for team_name, team_members in team_structure.items():
        for eid in team_members:
            employee = employees[eid - 1]
            employee.team = team_name
            team_graph.add_node(eid, team=team_name)

        for eid1, eid2 in itertools.combinations(team_members, 2):
            team_graph.add_edge(eid1, eid2)

    return team_graph

def create_friendships(employees, friendships):
    friendship_graph = nx.Graph()

    for eid1, eid2 in friendships:
        emp1 = employees[eid1 - 1]
        emp2 = employees[eid2 - 1]
        emp1.friends.add(emp2)
        emp2.friends.add(emp1)
        friendship_graph.add_edge(eid1, eid2)
    
    return friendship_graph


def generate_team_structure(num_employees, num_teams, min_team_size):
    employees_list = list(range(1, num_employees + 1))
    random.shuffle(employees_list)

    team_sizes = [min_team_size] * num_teams
    remaining_employees = num_employees - (min_team_size * num_teams)

    for i in range(remaining_employees):
        team_sizes[i % num_teams] += 1

    team_structure = {}
    for i in range(num_teams):
        team_name = f"Team{i + 1}"
        team_members = employees_list[:team_sizes[i]]
        employees_list = employees_list[team_sizes[i]:]
        team_structure[team_name] = team_members

    return team_structure

def generate_friendships(emps, num_friends):
    G = nx.barabasi_albert_graph(len(emps), num_friends)
    friendships = list(G.edges)
    return friendships
