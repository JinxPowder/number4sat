import api
import config
import time
import os
import glob
import re
from telethon import TelegramClient
import asyncio

loop = asyncio.get_event_loop()

client = TelegramClient('ADMIN2' , config.API_ID, config.API_HASH)
client.start()

while(True):
    files = glob.glob('Data/ZZZ*')
    for f in files:
        file = open(f,'r')
        lines = file.readlines()
        file.close()
        id = f[8:-4]
        user_id = lines[0].strip('\n')
        message_id = lines[1].strip('\n')
        pri = lines[2].strip('\n')

        status = api.check_status(id)
        if(status['DESCRIPTION']=="code received"):
            code = status['CODE']
            loop.run_until_complete(client.send_message("@"+config.Bot_Username,"/Code ("+user_id+")("+message_id+")("+code+")"))
            os.remove(f)
        elif(status['DESCRIPTION']=="wait code"):
            continue
        else:
            loop.run_until_complete(client.send_message("@"+config.Bot_Username,"/Cancel ("+user_id+")("+message_id+")("+pri+")"))
            os.remove(f)
        time.sleep(1)