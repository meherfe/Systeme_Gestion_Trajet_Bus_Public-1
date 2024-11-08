from process_manager import ProcessManager
from config import Config

def main():
    config = Config()
    config.generate_data()  # Generates the CSV file if it doesn't exist

    process_manager = ProcessManager(config)

    # Choose whether to run with multithreading or not
    use_multithreading = False  # Set to False for sequential processing

    # Start the processing (either sequential or multithreaded)
    process_manager.start_processes(use_multithreading)

if __name__ == "__main__":
    main()
