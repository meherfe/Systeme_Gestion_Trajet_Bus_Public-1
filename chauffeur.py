class Chauffeur:
    def __init__(self, driver_id, name, available=True):
        self.driver_id = driver_id
        self.name = name
        self.available = available

    def assign_bus(self, bus):
        if self.available:
            print(f"Chauffeur {self.name} assigned to bus {bus.bus_id}")
            self.available = False
            return True
        else:
            print(f"Chauffeur {self.name} is not available")
            return False

    def finish_trip(self):
        self.available = True
        print(f"Chauffeur {self.name} has finished the trip and is now available")
