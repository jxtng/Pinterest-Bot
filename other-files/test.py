from datetime import time, datetime as dt
from time import localtime

# print(dt.now().time()>dt(2023,1,1).time())
# print(dir(dt))

print(localtime().tm_hour)
