from threading import Thread, Semaphore, Lock

class Reservation:
    def __init__(self, bus):
        self.bus = bus
        self.seats = [True] * 10  # 10 available seats
        self.lock = Lock()  # Lock for precise control over seat reservation
        self.semaphore = Semaphore(2)  # Semaphore allowing up to 2 threads to access concurrently

    def reserve_seat(self, passenger):
        with self.semaphore:  # Semaphore to allow limited concurrent access
            with self.lock:  # Lock to ensure only one thread modifies seats at a time
                for i in range(len(self.seats)):
                    if self.seats[i]:
                        self.seats[i] = False
                        self.bus.add_passenger(passenger)
                        print(f"Passenger {passenger} reserved seat {i} on bus {self.bus.bus_id}")
                        return True
                print(f"No seats available for passenger {passenger} on bus {self.bus.bus_id}")
                return False

    def start_reservation(self, passengers):
        threads = []
        for passenger in passengers:
            thread = Thread(target=self.reserve_seat, args=(passenger,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
