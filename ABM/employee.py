import random
import math
import networkx as nx

class Employee:
    def __init__(self, eid, position, team, hierarchy_level, hierarchy_adjustment_factor):
        self.eid = eid
        self.position = position
        self.team = team
        self.hierarchy_level = hierarchy_level
        self.hierarchy_adjustment_factor = hierarchy_adjustment_factor
        self.loc = None
        self.info = set()
        self.friends = set()
        self.metrics_handler = None
        self.speed = 1
        self.target_space = None
        self.path = []


    def move(self, spaces, threshold, timestep):
        ## filter out full spaces and current location
        available_spaces = [space for space in spaces if not space.is_full() and space != self.loc]

        # filter spaces based on hierarchy level
        if self.hierarchy_level >= threshold:
            preferred_spaces = [space for space in available_spaces if space.stype in ["Workstation", "Quiet Area"]]
        else:
            preferred_spaces = [space for space in available_spaces if space.stype in ["Workstation", "Break Area"]]

        # Get the set of spaces where friends or teammates are present
        friend_spaces = {friend.loc for friend in self.friends}
        team_spaces = {teammate.loc for teammate in self.team}  

        # Combine the sets and filter out None values (if someone has not yet chosen a space)
        combined_spaces = list(filter(None, friend_spaces | team_spaces))

        # If there are spaces where friends or teammates are present, update the list of preferred spaces
        if combined_spaces:
            preferred_spaces = list(set(preferred_spaces) & set(combined_spaces))
    
        if not preferred_spaces:
            preferred_spaces = available_spaces

        ## filter out current location from preferred spaces
        if self.loc in preferred_spaces:
            preferred_spaces.remove(self.loc)

        # Calculate distance-based probabilities for preferred spaces
        def euclidean_distance(pos1, pos2):
            return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

        distances = [euclidean_distance(self.loc.position, space.position) if self.loc is not None else 1 for space in preferred_spaces]
        probabilities = [1 / d if d != 0 else 0 for d in distances]
        total_probability = sum(probabilities)
        probabilities = [p / total_probability for p in probabilities]

        # Select a new space based on calculated probabilities
        self.loc = random.choices(preferred_spaces, probabilities)[0]

        self.target_space = random.choices(preferred_spaces, probabilities)[0]

        # Compute path to target space using A* algorithm
        start_node = (self.loc.position[0], self.loc.position[1])
        end_node = (self.target_space.position[0], self.target_space.position[1])
        graph = nx.Graph(spaces)  # create graph of all spaces
        path = nx.astar_path(graph, start_node, end_node)

        self.path = path
        self.target_space = self.path.pop(0)


    def interact(self, other, team_graph, friendship_graph, timestep):
        if self.loc.stype == "Workstation" or self.loc.stype == "Meeting Room":
            info_sharing_prob = 0.6
        else:  # "Break Area"
            info_sharing_prob = 0.3

        # Adjust info_sharing_prob based on hierarchy level difference
        hierarchy_diff = abs(self.hierarchy_level - other.hierarchy_level)
        hierarchy_factor = 1 - (0.1 * hierarchy_diff)
        info_sharing_prob *= hierarchy_factor

        if random.random() < info_sharing_prob:
            if friendship_graph.has_edge(self.eid, other.eid) or team_graph.has_edge(self.eid, other.eid):
                self.share_info(other)
                self.metrics_handler.record_interaction(timestep, self.eid, other.eid)

    def share_info(self, other):
        self.info.update(other.info)
        other.info.update(self.info)

    def add_friend(self, other):
        self.friends.add(other)
        other.friends.add(self)
    
    def update_location(self):
        # If the employee has not yet reached the target space, move towards it
        if self.target_space is not None:
            x, y = self.loc.position
            target_x, target_y = self.target_space.position
            dx = target_x - x
            dy = target_y - y
            dist = math.sqrt(dx ** 2 + dy ** 2)

            if dist > 0:
                dx /= dist
                dy /= dist

                # Move towards the target space at the employee's speed
                x += dx * self.speed
                y += dy * self.speed

                # If the employee reaches the target space, update the current location
                if abs(x - target_x) < self.speed and abs(y - target_y) < self.speed:
                    self.loc.remove_occupant(self)
                    self.loc = self.target_space
                    self.loc.add_occupant(self)

                    # If there are more spaces in the path, update the target space to the next space in the path
                    if len(self.path) > 0:
                        self.target_space = self.path.pop(0)
                    else:
                        self.target_space = None
