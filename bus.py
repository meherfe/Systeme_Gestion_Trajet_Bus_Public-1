import time
from reservation import Reservation
from chauffeur import Chauffeur

def run_bus(queue, bus_data):
    bus_id = bus_data['bus_id']
    line_id = bus_data['line_id']
    stops = bus_data['stops']
    chauffeur_name = bus_data['chauffeur']

    bus = type('Bus', (object,), {'bus_id': bus_id, 'add_passenger': lambda self, passenger: None})()
    chauffeur = Chauffeur(bus_id, chauffeur_name)

    if chauffeur.assign_bus(bus):
        message = f"Bus {bus_id} is starting on line {line_id} with {chauffeur.name}"
        queue.put(message) if queue else print(message)

        for stop in stops:
            time.sleep(0.01)
            stop_message = f"Bus {bus_id} reached stop {stop}"
            queue.put(stop_message) if queue else print(stop_message)

        completion_message = f"Bus {bus_id} has completed its route."
        queue.put(completion_message) if queue else print(completion_message)

        chauffeur.finish_trip()

        reservation_system = Reservation(bus)
        passengers = [f"Passenger {i}" for i in range(1, 16)]
        reservation_system.start_reservation(passengers)
    else:
        failure_message = f"Bus {bus_id} could not start because chauffeur {chauffeur.name} is not available"
        queue.put(failure_message) if queue else print(failure_message)
