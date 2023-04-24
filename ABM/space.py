class Space:
    def __init__(self, sid, stype, capacity, position):
        self.sid = sid
        self.stype = stype
        self.capacity = capacity
        self.position = position
        self.occupants = []

    def add_occupant(self, employee):
        self.occupants.append(employee)

    def remove_occupant(self, employee):
        self.occupants.remove(employee)
        
    def is_full(self):
        return len(self.occupants) >= self.capacity

