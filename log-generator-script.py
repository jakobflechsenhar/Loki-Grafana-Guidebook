# -------------------------------------------------------- #
# log-generator-script.py
# -------------------------------------------------------- #

# Purpose: Simulates real applications generating logs
# What it does: Prints timestamped log entries with different severity levels (INFO, WARNING, ERROR)

import time, random

while True:
    level = random.choice(["INFO", "WARN", "ERROR"])
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {level} Something happened")
    time.sleep(1)   # Generate one log per second