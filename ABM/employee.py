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
        self.metrics_handler = None

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
