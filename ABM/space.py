class Space:
    def __init__(self, sid, stype, capacity):
        self.sid = sid
        self.stype = stype
        self.capacity = capacity
        self.occupants = []

    def add_occupant(self, employee):
        self.occupants.append(employee)

    def remove_occupant(self, employee):
        self.occupants.remove(employee)