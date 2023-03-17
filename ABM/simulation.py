import numpy as np
from employee import Employee
from space import Space
from social_graph import create_teams, create_friendships, generate_team_structure, generate_friendships

class InteractionHandler:
    def __init__(self, team_graph, friendship_graph):
        self.team_graph = team_graph
        self.friendship_graph = friendship_graph

    def handle_interactions(self, spaces):
        for space in spaces:
            occupants = space.occupants
            for i in range(len(occupants)):
                for j in range(i + 1, len(occupants)):
                    occupants[i].interact(occupants[j], self.team_graph, self.friendship_graph)


class MetricsHandler:
    def __init__(self, emps, spaces):
        self.emps = emps
        self.spaces = spaces

    def calculate_metrics(self):
        informed_count = sum(1 for e in self.emps if "Important Information" in e.info)
        informed_percentage = (informed_count / len(self.emps)) * 100
        return informed_count, informed_percentage

    def print_simulation_state(self, t, informed_count, informed_percentage):
        print(f"Time step {t + 1}")
        print(f"Informed employees: {informed_count}/{len(self.emps)} ({informed_percentage:.2f}%)")

        for space in self.spaces:
            print(f"Space {space.sid} ({space.stype}): {[e.eid for e in space.occupants]}")
        print(f"Information spread: {[e.eid for e in self.emps if 'Important Information' in e.info]}")
        print()


def initialize_simulation(num_employees, num_teams, min_team_size, num_friendships, num_spaces, space_types, space_capacities):
    team_structure = generate_team_structure(num_employees, num_teams, min_team_size)

    emps = [Employee(i, "Employee", None) for i in range(1, num_employees + 1)]

    team_graph = create_teams(emps, team_structure)

    friendships = generate_friendships(emps, num_friendships)
    friendship_graph = create_friendships(emps, friendships)

    spaces = [Space(i, space_types[i-1], space_capacities[i-1]) for i in range(1, num_spaces + 1)]

    return emps, spaces, team_graph, friendship_graph



def run_simulation(emps, spaces, time_steps, initial_info_holder, team_graph, friendship_graph):
    emps[initial_info_holder - 1].info.add("Important Information")

    interaction_handler = InteractionHandler(team_graph, friendship_graph)
    metrics_handler = MetricsHandler(emps, spaces)

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
        interaction_handler.handle_interactions(spaces)

        # Calculate and print metrics
        informed_count, informed_percentage = metrics_handler.calculate_metrics()
        metrics_handler.print_simulation_state(t, informed_count, informed_percentage)








