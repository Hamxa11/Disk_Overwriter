# README for Disk Overwriter

## Overview

**Disk Overwriter** is a Python script designed to **format and fill a selected drive** with random data until it is full. The script runs with administrative privileges and uses multithreading to optimize performance. It is useful for testing disk performance, securely overwriting sensitive data, or simulating scenarios where disk space is completely utilized.

## Features
- **Drive Detection**: Automatically detects and lists all available drives on the system.
- **Drive Formatting**: Formats the selected drive before writing data.
- **Random Data Writing**: Fills the drive with randomly generated data until it's full.
- **Multithreading**: Utilizes all available CPU cores for optimal performance.
- **Iterative Operation**: Optionally repeats the process multiple times (fill and format cycles).
- **Progress Monitoring**: Displays a progress bar to track how much data has been written to the drive.
- **Graceful Interruption**: Can be interrupted by the user with `Ctrl+C` without causing data corruption.

## Requirements
- Python 3.x
- Admin privileges (The script prompts to run with elevated permissions if necessary).
- Libraries:
  - `psutil` for system and disk information.
  - `tqdm` for progress bars.
  - `ctypes` for admin privileges and drive operations.
  - `ThreadPoolExecutor` from `concurrent.futures` for multithreading.
  - `logging` for logging messages and errors.

Install dependencies using the following command:

```bash
pip install psutil tqdm
```

## How to Use

### 1. Running the Script
Run the script with Python. If not run as an administrator, it will automatically attempt to re-launch itself with admin privileges.

```bash
python disk_overwriter.py
```

### 2. Selecting a Drive
The script detects and lists available drives. You will be prompted to select the drive you want to format and fill.

```text
Available drives:
0: C: (100.00 GB)
1: D: (500.00 GB)
Select a drive by index: 
```

### 3. Confirming Drive Overwrite
After selecting the drive, confirm the overwrite operation. **Disk Overwriter** will format and fill the drive with data, so proceed with caution.

```text
Are you sure you want to write data to D:? This will fill the drive completely. (yes/no): 
```

### 4. Specifying Iterations
You'll be prompted to enter how many times you want to fill and format the drive. Each iteration fills the drive and formats it again.

```text
Enter the number of iterations (how many times to fill and format the drive): 
```

### 5. Progress Monitoring
The script displays a progress bar as it writes data to the drive.

```text
Writing data: 50% [######################------] 200.0GB/400.0GB
```

### 6. Canceling the Operation
You can stop the operation at any time by pressing `Ctrl+C`. The script will handle the interruption gracefully.

### Example

```bash
python disk_overwriter.py
INFO - Formatting drive D:...
INFO - Starting iteration 1 of 2
Writing data: 75% [###############################---] 150.0GB/200.0GB
INFO - Drive is full.
INFO - Formatting drive D:...
```

## Notes

- **Admin Privileges**: The script requires admin rights to format drives. It will re-launch itself with elevated privileges if necessary.
- **Data Destruction**: This process completely wipes the selected drive. Ensure you have backups or are working on a non-critical drive.
- **Interruptions**: If the operation is interrupted, the drive will be left in its current state. Restarting will continue the process.

## License
This script is open-source and distributed under the MIT License. Feel free to modify and distribute it as needed.
