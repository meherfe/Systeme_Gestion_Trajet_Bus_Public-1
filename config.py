import random
import csv

class Config:
    def __init__(self):
        self.file_name = 'bus_data.csv'
        self.num_entries = 100000

    def generate_data(self):
        routes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        stops = ['Stop 1', 'Stop 2', 'Stop 3', 'Stop 4', 'Stop 5', 'Stop 6', 'Stop 7', 'Stop 8', 'Stop 9', 'Stop 10']

        with open(self.file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Bus ID', 'Route', 'Chauffeur', 'Stops'])  # Header

            for i in range(self.num_entries):
                bus_id = i + 1
                route = random.choice(routes)
                chauffeur = f'Chauffeur {random.randint(1, 100)}'
                route_stops = random.sample(stops, random.randint(3, len(stops)))

                writer.writerow([bus_id, route, chauffeur, ','.join(route_stops)])

# Automatically generate the data when Config is initialized
if __name__ == "__main__":
    config = Config()
    config.generate_data()
