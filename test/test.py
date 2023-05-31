from datetime import datetime

now = datetime.now()
current_time = now.strftime("%Y-%m-%d_%H:%M:%S")
print("Current Time =", current_time)