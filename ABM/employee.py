import random
import math

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

    def move(self, spaces):
        def euclidean_distance(pos1, pos2):
            return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)
        distances = [euclidean_distance(self.loc.position, space.position) if self.loc is not None else 1 for space in spaces]
        probabilities = [1 / d if d != 0 else 0 for d in distances]
        total_probability = sum(probabilities)
        probabilities = [p / total_probability for p in probabilities]
        self.loc = random.choices(spaces, probabilities)[0]

    def interact(self, other, team_graph, friendship_graph):
        if self.loc.stype == "Workstation" or self.loc.stype == "Meeting Room":
            info_sharing_prob = 0.9
        else:  # "Break Area"
            info_sharing_prob = 0.5

        # Adjust info_sharing_prob based on hierarchy level difference
        hierarchy_diff = abs(self.hierarchy_level - other.hierarchy_level)
        hierarchy_factor = 1 - (0.1 * hierarchy_diff)
        info_sharing_prob *= hierarchy_factor

        if random.random() < info_sharing_prob:
            if friendship_graph.has_edge(self.eid, other.eid) or team_graph.has_edge(self.eid, other.eid):
                self.share_info(other)

    def share_info(self, other):
        self.info.update(other.info)
        other.info.update(self.info)

    def add_friend(self, other):
        self.friends.add(other)
        other.friends.add(self)
