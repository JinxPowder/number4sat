from threading import Thread
import telegram
import telegram
import telegram.ext
from telegram import (ParseMode , KeyboardButton , ReplyKeyboardMarkup,InlineQueryResultArticle ,InlineQueryResultPhoto ,InlineQueryResultCachedAudio , InlineQueryResultAudio , InputTextMessageContent , ReplyKeyboardRemove ,InlineKeyboardButton, InlineKeyboardMarkup, Update)
from telegram.ext import (StringCommandHandler , PrefixHandler , InlineQueryHandler , Updater , CommandHandler , MessageHandler , RegexHandler, Filters , ConversationHandler , CallbackQueryHandler, CallbackContext)
import requests
import logging
import time
import config
import api
import unicodedata
import re
import math   
import qrcode
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Start the bot.
    Bot_token = config.Telegram_api
    updater = Updater(Bot_token , use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("Paid", message_handeler))
    dp.add_handler(CommandHandler("Cancel", message_handeler))
    dp.add_handler(CommandHandler("Code", message_handeler))
    dp.add_handler(MessageHandler(Filters.text, message_handeler))

    updater.start_polling()
    updater.idle()

def start(update, context: CallbackContext):
    message = update['message']['text']
    user_id = str(update['message']['chat']['id'])
    reply_markup = replymarkup(0)
    change_user_state(user_id,"start")
    return context.bot.send_message(chat_id=user_id , text = texts(0), reply_markup = reply_markup)

def message_handeler(update, context: CallbackContext):
    message = update['message']['text']
    user_id = str(update['message']['chat']['id'])
    user_state = get_user_state(user_id)

    regex = r"(\/Paid .+)"
    matches = re.match(regex, message, re.MULTILINE)
    if(matches):
        return Thread(target=send_phone_number, args=(update , context)).start() 
    regex = r"(\/Cancel .+)"
    matches = re.match(regex, message, re.MULTILINE)
    if(matches):
        return Thread(target=send_withdraw, args=(update , context)).start() 
    regex = r"(\/Code .+)"
    matches = re.match(regex, message, re.MULTILINE)
    if(matches):
        return Thread(target=send_code, args=(update , context)).start() 
    
    if(user_state == "start"):
        if(message == texts(1)):
            return Thread(target=platform_list, args=(update , context)).start()    
    if(user_state == "platforms"):
        return Thread(target=country_list, args=(update , context)).start()
    regex = r"choose_country_(\d+)"
    matches = re.match(regex, user_state, re.MULTILINE)
    if(matches):
        return Thread(target=send_invoice , args=(update, context, matches.group(1))).start()

def send_phone_number(update, context: CallbackContext):
    message = update['message']['text']
    regex = '\(.+?\)'
    match = re.findall(regex,message)
    user_id = int(match[0][1:-1])
    message_id = int(match[1][1:-1])
    service = match[2][1:-1]
    country = match[3][1:-1]
    operator = match[4][1:-1]
    pri = int(match[5][1:-1])
    number = api.get_number(service,country,operator)
    # print(number,service,country,operator)
    if(number['RESULT']!=1):
        # 
        withdraw = str(api.make_withdraw(pri))
        img = qrcode.make(withdraw)
        img.save(withdraw+".png")
        context.bot.send_photo(chat_id=user_id ,photo=open(withdraw+".png",'rb') ,caption="Sorry this number isnt available now. you can try again later. You can get your sats back by using this withdraw(or scanning).\n\n" + withdraw,reply_to_message_id=message_id)
        os.remove(str(withdraw)+".png")
    else:
        id = number['ID']
        num = "+"+number['AREACODE']+" "+number['NUMBER'][len(number['AREACODE']):]
        msg = context.bot.send_message(chat_id=user_id, text="Thanks for paying!\nPlace number in app to get code!\nnumber : "+num,reply_to_message_id=message_id)
        file = open("Data/ZZZ"+id+".txt","w")
        file.write(str(user_id)+'\n'+str(msg.message_id)+'\n'+str(pri)+'\n')
        file.close()
        return

def send_invoice(update, context: CallbackContext, service):
    message = update['message']['text']
    user_id = str(update['message']['chat']['id'])

    andis = 0
    for i in message:
        if(i == ':'):
            if(andis < 2):
                return country_list(update, context, cn=str(service))
            operator = (message[andis-2]).translate(str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹","0123456789"))
            break
        andis+=1
    country = country_code(message[3:andis-2])
    try:
        js = api.get_info(platform=service,country=country,operator=operator)
        if(js[0]["count"]=="0" or js[0]["count"]=="?"):
                context.bot.send_message(chat_id=user_id , text ="Sorry. This number isnt available any more.")
                return country_list(update, context, cn=str(service))
        pri = int(price(js[0]["amount"]))
    except:
        context.bot.send_message(chat_id=user_id , text ="Sorry. This number isnt available any more.")
        return country_list(update, context, cn=str(service))
    invoice = api.make_invoice(pri)
    
    file = open("Data/YYY"+invoice["payment_hash"]+".txt",'w')
    file.write(user_id+'\n'+str(update.message.message_id)+'\n'+str(time.time())+'\n'+service+'\n'+country+'\n'+operator+'\n'+str(pri)+'\n')#
    file.close()

    img = qrcode.make(invoice["payment_request"])
    img.save(str(invoice["payment_hash"])+".png")
    context.bot.send_photo(chat_id=user_id , photo = open(str(invoice["payment_hash"])+".png",'rb') , caption = "\nYou have 10 minutes to pay " + str(pri) +" sat: \n"+invoice["payment_request"],reply_to_message_id=update.message.message_id)
    os.remove(str(invoice["payment_hash"])+".png")
    return

def country_list(update, context: CallbackContext, cn="0"):
    message = update['message']['text']
    user_id = str(update['message']['chat']['id'])

    if(message == texts(4)):
        platform = "1"
    elif(message == texts(5)):
        platform = "3"
    elif(message == texts(6)):
        platform = "2"
    else:
        if(cn!="0"):
            platform = cn
        else:
            return context.bot.send_message(chat_id=user_id,text="Please choose one of Buttons!")
    try:
        file = open("Data/service"+platform+".txt", 'r')
        lines = file.readlines()
        file.close()
    except:
        time.sleep(0.5) # Fix it in future
        file = open("Data/service"+platform+".txt", 'r')
        lines = file.readlines()
        file.close()


    texts1 = []
    texts2 = []
    bl = 1
    for line in lines:
        text = line.strip('\n')
        regex = '\(.+?\)'
        match = re.findall(regex,text)
        if(bl==1):
            texts1.append(match[0][1:-1] +" "+emoji_name(match[1][1:-1])+match[2][1:-1].translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))+" : "+price(match[3][1:-1])+" sat")
            bl=2
        elif(bl==2):
            texts2.append(match[0][1:-1] +" "+emoji_name(match[1][1:-1])+match[2][1:-1].translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))+" : "+price(match[3][1:-1])+" sat")
            bl=1
    reply=[]
    for i in range(len(texts2)):
        reply.append([KeyboardButton(texts1[i]),KeyboardButton(texts2[i])])
    if(bl==2):
        reply.append([KeyboardButton(texts1[len(texts1)-1])])

    reply_markup = ReplyKeyboardMarkup(reply, resize_keyboard = True)
    change_user_state(user_id,"choose_country_"+platform)
    context.bot.send_message(chat_id=user_id , text = "Choose one of this countries.", reply_markup = reply_markup)

def platform_list(update, context: CallbackContext):
    message = update['message']['text']
    user_id = str(update['message']['chat']['id'])
    reply_markup = replymarkup(1)
    change_user_state(user_id, "platforms")
    return context.bot.send_message(chat_id=user_id , text = texts(3), reply_markup = reply_markup)

def send_withdraw(update, context: CallbackContext):
    message = update['message']['text']
    regex = '\(.+?\)'
    match = re.findall(regex,message)
    user_id = int(match[0][1:-1])
    message_id = int(match[1][1:-1])
    pri = match[2][1:-1]

    withdraw = str(api.make_withdraw(pri))
    img = qrcode.make(withdraw)
    img.save(withdraw+".png")
    context.bot.send_photo(chat_id=user_id ,photo=open(withdraw+".png",'rb') ,caption="We dont recive any code. You can get your sats back by using this withdraw.\n\n" + withdraw,reply_to_message_id=message_id)
    os.remove(str(withdraw)+".png")
    return

def send_code(update, context: CallbackContext):
    message = update['message']['text']
    regex = '\(.+?\)'
    match = re.findall(regex,message)
    user_id = match[0][1:-1]
    message_id = match[1][1:-1]
    code = match[2][1:-1]
    context.bot.send_message(chat_id=user_id,text="code: "+code,reply_to_message_id=int(message_id))

def price(string):
    sat = int(string)*13/10
    return str(math.ceil(sat/10))

def get_user_state(user_id):
    file = open('userstate/' + user_id + '.txt', 'r')
    return (file.readlines())[0]

def change_user_state(user_id, user_state):
    file = open('userstate/' + user_id + '.txt', 'w')
    file.write(user_state)
    file.close()
    return

def texts(integer):
    text = [
        "Hello, welcome to LNnumbot. Where you can buy virtual numbers with Lightening!", #0
        "Buy Number", #1
        "Recive Balance", #2
        "Choose platform that you want to buy virtual number for.", #3
        "💎 Telegram", #4
        "✳️ WhatsApp", #5
        "🚀 Instagram", #6
    ]
    return text[integer]

def replymarkup(integer):
    replys = [
        ReplyKeyboardMarkup([
        [KeyboardButton(text=texts(1))],
        ] , resize_keyboard = True),

        ReplyKeyboardMarkup([
        [KeyboardButton(text=texts(4))],
        [KeyboardButton(text=texts(5)),KeyboardButton(text=texts(6))],
        ] , resize_keyboard = True),
    ]
    return replys[integer]

def country_code(string):
    if(string == "Russia"):
        return "1"
    if(string == "Ukraine"):
        return "2"
    if(string == "Kazakhstan"):
        return "3"
    if(string == "China"):
        return "4"
    if(string == "Philippines"):
        return "5"
    if(string == "Myanmar"):
        return "6"
    if(string == "Indonesia"):
        return "7"
    if(string == "Malaysia"):
        return "8"
    if(string == "Kenya"):
        return "9"
    if(string == "Tanzania"):
        return "10"
    if(string == "Vietnam"):
        return "11"
    if(string == "England"):
        return "12"
    if(string == "Latvia"):
        return "13"
    if(string == "Romania"):
        return "14"
    if(string == "Estonia"):
        return "15"
    if(string == "United States"):
        return "16"
    if(string == "Premium United States"):
        return "17"
    if(string == "Kyrgyzstan"):
        return "18"
    if(string == "France"):
        return "19"
    if(string == "Palestine"):
        return "20"
    if(string == "Cambodia"):
        return "21"
    if(string == "Macao"):
        return "22"
    if(string == "Hong Kong"):
        return "23"
    if(string == "Brazil"):
        return "24"
    if(string == "Poland"):
        return "25"
    if(string == "Paraguay"):
        return "26"
    if(string == "Netherlands"):
        return "27"
    if(string == "Lithuania"):
        return "28"
    if(string == "Madagascar"):
        return "29"
    if(string == "Congo"):
        return "30"
    return string

def emoji_name(string):
    if(string == "1"):
        return "Russia"
    if(string == "2"):
        return "Ukraine"
    if(string == "3"):
        return "Kazakhstan"
    if(string == "4"):
        return "China"
    if(string == "5"):
        return "Philippines"
    if(string == "6"):
        return "Myanmar"
    if(string == "7"):
        return "Indonesia"
    if(string == "8"):
        return "Malaysia"
    if(string == "9"):
        return "Kenya"
    if(string == "10"):
        return "Tanzania"
    if(string == "11"):
        return "Vietnam"
    if(string == "12"):
        return "England"
    if(string == "13"):
        return "Latvia"
    if(string == "14"):
        return "Romania"
    if(string == "15"):
        return "Estonia"
    if(string == "16"):
        return "United States"
    if(string == "17"):
        return "Premium United States"
    if(string == "18"):
        return "Kyrgyzstan"
    if(string == "19"):
        return "France"
    if(string == "20"):
        return "Palestine"
    if(string == "21"):
        return "Cambodia"
    if(string == "22"):
        return "Macao"
    if(string == "23"):
        return "Hong Kong"
    if(string == "24"):
        return "Brazil"
    if(string == "25"):
        return "Poland"
    if(string == "26"):
        return "Paraguay"
    if(string == "27"):
        return "Netherlands"
    if(string == "28"):
        return "Lithuania"
    if(string == "29"):
        return "Madagascar"
    if(string == "30"):
        return "Congo"
    return string

if __name__ == '__main__':
    main()