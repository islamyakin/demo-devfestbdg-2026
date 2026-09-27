import os
os.remove("/app/data/customers.txt")
print("customers.txt dihapus. ls /app/data ->", os.listdir("/app/data"))
