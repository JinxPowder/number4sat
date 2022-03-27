import config
import requests
import json

API_CODE = config.Numberland_api
headers = config.HEADERS
INVOICE_KEY = config.Invoice_read_key
ADMIN_KEY = config.Admin_key
WALLET_ID = config.Wallet_ID

def get_number(SERVICE_CODE,COUNTRY_CODE,OPERATOR_CODE): # Done
    response = requests.post("https://api.numberland.ir/v2.php/?apikey="+API_CODE+"&method=getnum&country="+COUNTRY_CODE+"&operator="+OPERATOR_CODE+"&service="+SERVICE_CODE ,headers=headers)
    todos = json.loads(response.text)
    
    try:
        info = todos
    except:
        info = -1
    return info

def check_status(ID): # Done
    response = requests.post("https://api.numberland.ir/v2.php/?apikey="+API_CODE+"&method=checkstatus&id="+ID ,headers=headers)
    todos = json.loads(response.text)
    
    try:
        info = todos
    except:
        info = -1
    return info

def change_status(ID,METHOD_NAME): # Done
    response = requests.post("https://api.numberland.ir/v2.php/?apikey="+API_CODE+"&method="+METHOD_NAME+"&id="+ID ,headers=headers)
    todos = json.loads(response.text)
    
    try:
        info = todos
    except:
        info = -1
    return info

def balance(): # Done
    response = requests.post('https://api.numberland.ir/v2.php/?apikey='+API_CODE+'&method=balance',headers=headers)
    todos = json.loads(response.text)

    try:
        balance = todos['BALANCE']
    except:
        balance = -1
    return balance

def get_info(platform="any", country="any", operator="any"): # Done
    response = requests.post('https://api.numberland.ir/v2.php/?apikey='+API_CODE+'&method=getinfo&service='+str(platform)+'&operator='+str(operator)+'&country='+str(country),headers=headers)
    todos = json.loads(response.text)
    
    try:
        info = todos
    except:
        info = -1
    return info

def make_invoice(amount): # Done
    invoice = requests.post("https://legend.lnbits.com/api/v1/payments", data = '{"out": false,"amount":'+str(amount)+'}', headers = {"X-Api-Key": INVOICE_KEY,"Content-type": "application/json"})
    js = invoice.json()
    return js

def make_withdraw(amount): # Done
    withdraw = requests.post("https://legend.lnbits.com/withdraw/api/v1/links", data = '{"title": "Hi", "min_withdrawable": '+str(amount)+', "max_withdrawable": '+str(amount)+', "uses": 1, "wait_time": 1, "is_unique": true}' , headers = {"X-Api-Key": ADMIN_KEY,"Content-type": "application/json"})
    js = withdraw.json()
    return js["lnurl"]

def check_invoice(payment_hash): # Done
    check = requests.get("https://legend.lnbits.com/api/v1/payments/"+payment_hash, headers = {"X-Api-Key": INVOICE_KEY,"Content-type": "application/json"})
    js = check.json()
    return js["paid"]

