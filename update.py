import api
import config
import time
import os
import glob
import re

while(True):
    # update service files
    print(time.time())
    js = api.get_info()
    print(time.time())
    files = glob.glob('Data/service*')
    for f in files:
        os.remove(f)
    for i in js:
        service = i["service"]
        country = i["country"]
        operator = i["operator"]
        count = i["count"]
        amount = i["amount"]
        emoji = i["emoji"]

        if(count == "?"):
            continue
        if(count == "0"):
            continue
        
        file = open("Data/service"+service+'.txt' , 'a')
        file.write("("+emoji+")("+country+")("+operator+")("+amount+")\n")
        file.close()
    # print(time.time())
    print("done")
    time.sleep(60)


