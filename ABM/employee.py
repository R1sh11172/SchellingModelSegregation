import random

class Employee:
    def __init__(self, eid, position, team):
        self.eid = eid
        self.position = position
        self.team = team
        self.loc = None
        self.info = set()
        self.friends = set()

    def move(self, spaces):
        self.loc = random.choice(spaces)

    def interact(self, other, team_graph, friendship_graph):
        if self.loc.stype == "Workstation" or self.loc.stype == "Meeting Room":
            info_sharing_prob = 0.9
        else:  # "Break Area"
            info_sharing_prob = 0.5

        if random.random() < info_sharing_prob:
            if friendship_graph.has_edge(self.eid, other.eid) or team_graph.has_edge(self.eid, other.eid):
                self.share_info(other)

    def share_info(self, other):
        self.info.update(other.info)
        other.info.update(self.info)

    def add_friend(self, other):
        self.friends.add(other)
        other.friends.add(self)
