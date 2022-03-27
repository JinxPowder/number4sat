import api
import config
import time
import os
import glob
import re
from telethon import TelegramClient
import asyncio

loop = asyncio.get_event_loop()

client = TelegramClient('ADMIN' , config.API_ID, config.API_HASH)
client.start()

while(True):
    files = glob.glob('Data/YYY*')
    for f in files:
        file = open(f,'r')
        lines = file.readlines()
        file.close()
        payment_hash = f[8:-4]
        user_id = lines[0].strip('\n')
        message_id = lines[1].strip('\n')
        times = lines[2].strip('\n')
        service = lines[3].strip('\n')
        country = lines[4].strip('\n')
        operator = lines[5].strip('\n')
        pri = lines[6].strip('\n')
        if(api.check_invoice(payment_hash)==True):
            loop.run_until_complete(client.send_message("@"+config.Bot_Username,"/Paid ("+user_id+")("+message_id+")("+service+")("+country+")("+operator+")("+pri+")"))
            os.remove(f)
        elif(time.time()-float(times)>(12*60)):
            os.remove(f)
    time.sleep(1)
