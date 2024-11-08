import time
import os
import csv
import psutil
from multiprocessing import Process, cpu_count
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from bus import run_bus  # Ensure `run_bus` is compatible with multiprocessing

# Thread-safe print function to avoid message overlap
print_lock = Lock()
def safe_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)

class ProcessManager:
    def __init__(self, config):
        self.config = config

    def load_data_from_csv(self, file_name):
        bus_data_list = []
        with open(file_name, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                bus_data = {
                    'bus_id': row['Bus ID'],
                    'line_id': row['Route'],
                    'chauffeur': row['Chauffeur'],
                    'stops': row['Stops'].split(','),
                }
                bus_data_list.append(bus_data)
        return bus_data_list

    def process_multithreaded(self, bus_data_list):
        # Using max_workers equal to twice the CPU count, for instance, to allow parallelism
        max_workers = cpu_count() * 2
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for bus_data in bus_data_list:
                executor.submit(run_bus, None, bus_data)
        return max_workers

    def process_multiprocessing(self, bus_data_list):
        processes = []
        for index, bus_data in enumerate(bus_data_list):
            process = Process(target=run_bus, args=(None, bus_data))
            processes.append(process)
            process.start()

            # Limit the number of active processes to the number of CPU cores
            if len(processes) >= cpu_count():
                for p in processes:
                    p.join()  # Ensure each batch completes before starting more
                processes = []  # Clear completed processes

        # Join any remaining processes
        for process in processes:
            process.join()

    def start_processes(self, use_multithreading=False):
        bus_data_list = self.load_data_from_csv('bus_data.csv')
        start_time = time.time()
        cpu_usage_start = psutil.cpu_percent(interval=None)

        if use_multithreading:
            safe_print("Processing with multithreading...")
            num_threads_used = self.process_multithreaded(bus_data_list)
        else:
            safe_print("Processing sequentially with multiprocessing...")
            self.process_multiprocessing(bus_data_list)
            num_threads_used = 1  # Typically, only one main process manages workers in this mode

        end_time = time.time()
        cpu_usage_end = psutil.cpu_percent(interval=None)
        avg_cpu_usage = (cpu_usage_start + cpu_usage_end) / 2

        # Display summary information
        safe_print(f"Processing Time: {end_time - start_time:.2f} seconds")
        safe_print(f"Average CPU Usage: {avg_cpu_usage}%")
        safe_print(f"Number of Threads Used: {num_threads_used}")
        safe_print(f"Number of CPU Cores: {cpu_count()}")
