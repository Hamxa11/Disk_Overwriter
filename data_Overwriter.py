import os
import ctypes
import psutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import signal
import multiprocessing
import logging
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        try:
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
            sys.exit()
        except:
            print("Failed to acquire administrative privileges.")
            #ctypes.windll.user32.MessageBoxW(0, "Failed to acquire administrative privileges.", "Error", 0x10)
            #sys.exit()

def list_drives():
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for i in range(26):
        if bitmask & (1 << i):
            drive = chr(65 + i) + ":"
            try:
                usage = psutil.disk_usage(drive)
                total_gb = usage.total / (1024 ** 3)
                drives.append((drive, total_gb))
            except Exception as e:
                logging.error(f"Could not get size for drive {drive}: {e}")
    return drives

def format_drive(drive):
    try:
        logging.info(f"Formatting drive {drive}...")
        command = f'format {drive} /FS:NTFS /Q /Y'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"Failed to format drive {drive}. Try running with administrative privileges.")
        else:
            logging.info(f"Drive {drive} formatted successfully.")
    except Exception as e:
        logging.error(f"Error formatting drive {drive}: {e}")

def write_random_data_to_drive(drive, iterations=1):

    format_drive(drive)
 
    for iteration in range(iterations):
        logging.info(f"Starting iteration {iteration + 1} of {iterations}")

        total_size = psutil.disk_usage(drive).total
        free_size = psutil.disk_usage(drive).free
        progress_bar = tqdm(total=free_size, unit='B', unit_scale=True, desc='Writing data', dynamic_ncols=True)
        should_stop = multiprocessing.Value('b', False)

        def signal_handler(sig, frame):
            should_stop.value = True
            logging.info("\nStopping...")

        signal.signal(signal.SIGINT, signal_handler)

        try:
            file_count = multiprocessing.Value('i', 0)
            max_workers = os.cpu_count() 
            optimal_workers = max_workers
            min_workers = 1

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                while not should_stop.value and psutil.disk_usage(drive).free > 0:
                    free_space = psutil.disk_usage(drive).free
                    if free_space < 1024:
                        break

                    data_size = min(1 * 1024 * 1024, free_space)
                    if data_size < 1:
                        break

                    future = executor.submit(write_random_file, drive, file_count.value, data_size)
                    futures.append(future)
                    with file_count.get_lock():
                        file_count.value += 1

                    if len(futures) > max_workers:
                        for future in as_completed(futures):
                            try:
                                future.result()
                            except Exception as e:
                                logging.error(f"Error during future execution: {e}")
                        futures = [f for f in futures if not f.done()]

                    new_free_size = psutil.disk_usage(drive).free
                    progress_bar.update(free_size - new_free_size)
                    free_size = new_free_size

                    if free_size < total_size * 0.1: 
                        optimal_workers = min_workers
                    else:
                        optimal_workers = max_workers

                    executor._max_workers = optimal_workers

                # for future in as_completed(futures):
                #     try:
                #         future.result()  
                #     except Exception as e:
                #         logging.error(f"Error during future execution: {e}")

                if should_stop.value:
                    logging.info("Process was stopped by the user.")
                else:
                    logging.info("Drive is full.")

        except Exception as e:
            logging.error(f"Stopped writing data: {e}")
        finally:
            progress_bar.close()

        #if iteration < iterations - 1:  
            format_drive(drive)

def write_random_file(drive, file_count, data_size):
    #try:
        file_path = Path(drive) / f"random_data_{file_count}"
        with open(file_path, "wb", buffering=1024 * 1024) as f: 
            f.write(os.urandom(data_size))
    #except OSError as e:
        # if e.errno == 28: 
        #     logging.warning(f"Drive is full: {e}")
        # else:
        #     logging.error(f"Error writing file {file_path}: {e}")

def main():
    run_as_admin()
    
    drives = list_drives()
    if not drives:
        logging.info("No drives found.")
        return

    logging.info("Available drives:")
    for i, (drive, size) in enumerate(drives):
        logging.info(f"{i}: {drive} ({size:.2f} GB)")

    try:
        selected_index = int(input("Select a drive by index: "))
        if selected_index < 0 or selected_index >= len(drives):
            logging.warning("Invalid drive index selected.")
            return

        selected_drive = drives[selected_index][0]
        confirm = input(f"Are you sure you want to write data to {selected_drive} This will fill the drive completely. (yes/no): ")

        if confirm.lower() == 'yes':
            try:
                iterations = int(input("Enter the number of iterations (how many times to fill and format the drive): "))
                if iterations <= 0:
                    raise ValueError("Iterations must be a positive integer.")
            except ValueError as e:
                logging.error(f"Invalid input for iterations: {e}")
                return

            write_random_data_to_drive(selected_drive, iterations)
        else:
            logging.info("Operation cancelled.")

    except ValueError:
        logging.warning("Invalid input. Please enter a number corresponding to the drive index.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
	
