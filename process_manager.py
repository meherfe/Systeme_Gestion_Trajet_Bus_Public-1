ssimport time
import os
import csv
import psutil
from multiprocessing import Process, Pipe, cpu_count
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

    def process_with_threads(self, bus_data_list):
        # Execute each bus simulation sequentially, no threads or pool
        for bus_data in bus_data_list:
            run_bus(None, bus_data)
        return 1  # One thread used

    def process_with_thread_pool(self, data_chunk, max_workers, conn):
        # Multi-threaded execution within a single process
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(run_bus, None, bus_data) for bus_data in data_chunk]
            for future in futures:
                future.result()  # Wait for each thread to complete
                conn.send("Bus processed successfully.")
        conn.close()  # Close the connection after processing

    def process_multiprocessing_with_threads(self, bus_data_list):
        num_processes = cpu_count()
        chunk_size = len(bus_data_list) // num_processes
        chunks = [bus_data_list[i * chunk_size: (i + 1) * chunk_size] for i in range(num_processes)]
        
        processes = []
        parent_conns = []
        for chunk in chunks:
            parent_conn, child_conn = Pipe()
            process = Process(target=self.process_with_thread_pool, args=(chunk, cpu_count(), child_conn))
            processes.append(process)
            parent_conns.append(parent_conn)
            process.start()

        # Ensure all processes complete and collect messages
        for process, parent_conn in zip(processes, parent_conns):
            process.join()  # Wait for the process to complete
            try:
                while parent_conn.poll():  # Check for any remaining messages
                    message = parent_conn.recv()
                    safe_print(message)
            except BrokenPipeError:
                # Handle the pipe being closed by the child process
                safe_print("Pipe was closed by the child process.")
            finally:
                parent_conn.close()  # Ensure connection is closed after reading

        return num_processes * cpu_count()  # Total threads used across all processes

    def start_processes(self, use_multithreading=False):
        bus_data_list = self.load_data_from_csv('bus_data.csv')
        start_time = time.time()
        cpu_usage_start = psutil.cpu_percent(interval=None)

        if use_multithreading:
            safe_print("Processing with multithreading (multiple processes and threads)...")
            num_threads_used = self.process_multiprocessing_with_threads(bus_data_list)
        else:
            safe_print("Processing sequentially (single process, single thread)...")
            num_threads_used = self.process_with_threads(bus_data_list)

        end_time = time.time()
        cpu_usage_end = psutil.cpu_percent(interval=None)
        avg_cpu_usage = (cpu_usage_start + cpu_usage_end) / 2

        # Display summary information
        safe_print(f"Processing Time: {end_time - start_time:.2f} seconds")
        safe_print(f"Average CPU Usage: {avg_cpu_usage}%")
        safe_print(f"Number of Threads Used: {num_threads_used}")
        safe_print(f"Number of CPU Cores: {cpu_count()}")
