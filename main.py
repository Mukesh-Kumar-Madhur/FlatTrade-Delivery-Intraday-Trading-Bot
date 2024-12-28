## This is a script which trades 2 time morning and evening and live monitor for the price whole day and exit order.
################============ F L A T - T R A D E =================########################
from urllib.parse import parse_qs, urlparse
from NorenRestApiPy.NorenApi import NorenApi
from datetime import datetime, timedelta
import time
import pandas as pd
import pyotp
import requests
import hashlib
import threading
import login as l
import mail 
import database as db


## Fund for each stock this will be multiplied by the leverage
## this is ACTUAL CAPITAL WITHOUT LEVERAGE
day_open_fund = 650
day_end_fund = 25000


## Time Paramaters:-
trade_time_evening = datetime.strptime("15:29:57", "%H:%M:%S").time()
trade_stop_time_evening = datetime.strptime("15:30:01", "%H:%M:%S").time()
trade_time_morning = datetime.strptime("09:15:00", "%H:%M:%S").time()
trade_stop_time_morning = datetime.strptime("09:15:15", "%H:%M:%S").time()

## This is the dict of all the stocks , make sure to remove "#" from those stocks, which you want today to place order for
## Make sure to use MIS in the morning only!!

stocks = {
    # "ABCAPITAL-EQ": "MIS", 
    # "CESC-EQ": "MIS", 
    # "HAL-EQ": "MIS",
    # "HINDCOPPER-EQ": "MIS", 
    # "TITAN-EQ": "MIS", 
    # "CYIENT-EQ": "MIS", 
    "SONACOMS-EQ": "MIS", 
    # "CDSL-EQ": "MIS", 
    # "TATAELXSI-EQ": "MIS", 
    # "CANFINHOME-EQ": "MIS", 

    # "EDELWEISS-EQ": "MTF",
    # "NH-EQ": "MTF",
    # "TEJASNET-EQ": "MTF",
    # "GRAVITA-EQ": "MTF",
    # "KCP-EQ": "MTF",
    # "NATCOPHARM-EQ": "MTF",
    # "SCHNEIDER-EQ": "MTF",
    # "GESHIP-EQ": "MTF",
    # "LATENTVIEW-EQ": "MTF",
    # "MAPMYINDIA-EQ": "MTF",
    # "MOLDTECH-EQ": "MTF",
    # "INGERRAND-EQ": "MTF",
    # "MAZDOCK-EQ": "MTF",
    # "JMFINANCIL-EQ": "MTF",
    # "ACE-EQ": "MTF",
    # "ROHLTD-EQ": "MTF",
    # "TRITURBINE-EQ": "MTF",
    # "TBOTEK-EQ": "MTF",
    # "VPRPL-EQ": "MTF"
}


## this function will return the value of the stocks dict.
def get_product_type  (stock_key):
    # Corrected stocks dictionary
    dict = stocks
    # Retrieve the value for the provided key
    return dict.get(stock_key, "CNC")


# Load credentials and configurations
APIKEY = l.Api_Key
secretKey = l.Api_Secret_Key
totp_key = l.Totp
password = l.Client_Pass
userid = l.Client_ID
headerJson = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36",
    "Referer": "https://auth.flattrade.in/"
}

# Generate TOTP
# otp = pyotp.TOTP(totp_key).now()
# print("Otp is:", otp)
print("Starting Login Process...")

# Retry configuration
max_retries = 3
retry_delay = 5  # seconds

token = None
def login():
    retries = 0
    while retries < max_retries:
        try:
            # Generate Token
            ses = requests.Session()
            sesUrl = 'https://authapi.flattrade.in/auth/session'
            passwordEncrpted = hashlib.sha256(password.encode()).hexdigest()

            res_pin = ses.post(sesUrl, headers=headerJson)
            sid = res_pin.text
            print(f'sid {sid}')

            url2 = 'https://authapi.flattrade.in/ftauth'
            payload = {
                "UserName": userid,
                "Password": passwordEncrpted,
                "PAN_DOB": pyotp.TOTP(totp_key).now(),
                "App": "",
                "ClientID": "",
                "Key": "",
                "APIKey": APIKEY,
                "Sid": sid,
                "Override": "Y",
                "Source": "AUTHPAGE"
            }
            res2 = ses.post(url2, json=payload)
            reqcodeRes = res2.json()
            print(reqcodeRes)

            parsed = urlparse(reqcodeRes['RedirectURL'])
            reqCode = parse_qs(parsed.query)['code'][0]
            api_secret = APIKEY + reqCode + secretKey
            api_secret = hashlib.sha256(api_secret.encode()).hexdigest()

            payload = {"api_key": APIKEY, "request_code": reqCode, "api_secret": api_secret}
            url3 = 'https://authapi.flattrade.in/trade/apitoken'
            res3 = ses.post(url3, json=payload)
            print(res3.json())

            global token
            token = res3.json()['token']

            # Create Broker Object
            class FlatTradeApiPy(NorenApi):
                def __init__(self):
                    NorenApi.__init__(self, host='https://piconnect.flattrade.in/PiConnectTP/',
                                        websocket='wss://piconnect.flattrade.in/PiConnectWSTp/',
                                        eodhost='https://web.flattrade.in/chartApi/getdata/')

            global api, ret
            api = FlatTradeApiPy()
            ret = api.set_session(userid=userid, password=password, usertoken=token)

            print("Login successful.")
            return True  # Return True on success

        except Exception as e:
            print(f"Login Failed: {e}")
            retries += 1
            if retries < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Login failed.")
                return False  # Return False after max retries


# Create Broker Object
class FlatTradeApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://piconnect.flattrade.in/PiConnectTP/',
                            websocket='wss://piconnect.flattrade.in/PiConnectWSTp/',
                            eodhost='https://web.flattrade.in/chartApi/getdata/')

api = FlatTradeApiPy()
ret = api.set_session(userid=userid, password=password, usertoken=token)


# Function to login and check login
def is_login():
    if login():
        return True
    else:
        return False

def is_weekday():
    current_day = datetime.now().weekday()
    return 0 <= current_day <= 4

if is_login():
    print("")

################ F U N C T I O N S :-
def modify_prct_type():
    pass

def fetch_ltp(symbol):
    try:
        token_response = api.searchscrip(exchange='NSE', searchtext=symbol)
        if token_response.get('stat') == 'Ok' and isinstance(token_response.get('values'), list):
            token = token_response['values'][0]['token']
            ltp_response = api.get_quotes(exchange='NSE', token=token)
            return float(ltp_response['lp'])
        else:
            raise ValueError("Failed to fetch LTP: Invalid response")
    except Exception as e:
        print(f"Error fetching LTP for {symbol}: {str(e)}")
        return None


def is_mis(symbol):
    df = pd.read_excel("Margins.xlsx", skiprows=1)
    df = df.drop(columns=['MIS/CO/BO.1', 'MTF.1'])
    df = df.dropna()  # Remove all records where rows are NA for MIS or NTF or any
    symbol = symbol.split('-')[0]  # Remove "-EQ" from the symbol
    
    ## Make sure it is morning time, because planning MIS for morning order only
    current_time = datetime.now()
    cutoff_time = current_time.replace(hour=9, minute=16, second=0, microsecond=0)
    
    if df['SYMBOL'].str.lower().eq(symbol.lower()).any() and current_time < cutoff_time:
        return True
    else:
        return False



def exit_order(symbol, Qty):
    ltp_price = fetch_ltp(symbol)
    
    ## Deciding Product type
    if get_product_type(symbol) == "MIS":
        MIS_or_MTF = "I"
    elif get_product_type(symbol) == "MTF":
        MIS_or_MTF = "F"  ## Change "F" to "C" if we want CNC order
    else : 
        MIS_or_MTF = "C"
    
    if ltp_price is None:
        print(f"Failed to fetch LTP for {symbol}. Skipping order.")
        return None

    try:
        ret  = api.place_order(
            act_id        =  l.Client_ID,   
            buy_or_sell   =  'S',
            product_type  =  MIS_or_MTF,  ## We are going to use  MTF-F or MIS-I
            exchange      =  'NSE',
            tradingsymbol =  symbol,
            quantity      =  Qty, 
            discloseqty   =  0,
            price_type    =  'MKT',
            price         =   0,
            trigger_price =  None,
            retention     =  'DAY',
            remarks       =  f'Placed a Sell order to exit {symbol} position '
        )
        print(f"Order placed successfully for {symbol}:", ret)
        return ret
    except Exception as e:
        print(f"Failed to place order for {symbol}: {str(e)}")
        return None


def place_order(symbol,Qty):

    ## Deciding Product type
    if get_product_type(symbol) == "MIS":
        MIS_or_MTF = "I"
    elif get_product_type(symbol) == "MTF":
        MIS_or_MTF = "F"  ## Change "F" to "C" if we want CNC order
    else : 
        MIS_or_MTF = "C"
    
    try:
        ret = api.place_order(
            act_id=l.Client_ID,   
            buy_or_sell='B',
            product_type= MIS_or_MTF,  
            exchange='NSE',
            tradingsymbol=symbol,
            quantity=Qty,
            discloseqty=0,
            price_type='MKT',
            price=0,
            trigger_price=None,
            retention='DAY',
            remarks='Order placed via script'
        )
        print(f"Order placed successfully for {symbol}:", ret)
        return ret
    except Exception as e:
        print(f"Failed to place order for {symbol}: {str(e)}")
        return None



def live_monitor(symbol):
    while True:  # In Case of threading
        
        try:
            ltp = fetch_ltp(symbol)
            ltp = float(ltp)
            print(f"Monitoring: {symbol} | Ltp: {ltp}")
        except:
            print(f"Failed to fetch LTP of {symbol}")
            time.sleep(2.5)
            continue  # Skip the rest of the loop and try again
        
        ## Fetch qty from the database, so that exit will be same as placed qty.
        qty = db.get_qty(symbol, ltp)

        if int(qty) > 0:
            # if is_mis():  # Exit MIS order
            order = exit_order(symbol, qty)
            if order:
                print(f"Order Exit Successfully {symbol}, Qty: {qty}")
                db.db_exit(symbol, ltp)  # Make exit entry into db
                mail.mail_with_text(f"Order Completed {symbol}", f"A Order has been completed and Exit made\n\n Symbol: {symbol}  \nExit_price: {ltp} \nQuantity: {qty}")
                break  # Exit the main while loop after successful order exit
            # else:  # Exit MTF or CNC order
            #     order = exit_order(symbol, qty)
            #     if order:
            #         print(f"Order Exit Successfully {symbol}, Qty: {qty}")
            #         db.db_exit(symbol, ltp)  # Make exit entry into db
            #         mail.mail_with_text(f"Order Completed {symbol}", f"A Order has been completed and Exit made\n\n Symbol: {symbol}  \nExit_price: {ltp} \nQuantity: {qty}")
            #         break  # Exit the main loop after successful order exit
        time.sleep(2)



def place_order_in_thread(symbol):
    
    ltp = fetch_ltp(symbol)
    if ltp is not None:
        if is_mis(symbol) or get_product_type(symbol) == 'MIS':
            qntty = int((day_open_fund*5) // ltp)
        elif get_product_type == "MTF":
            qntty = int((day_end_fund*3) // ltp)
        else:
            qntty = int((day_end_fund)//ltp)
        
    if place_order(symbol,qntty):
        print(f"Order placed for {symbol} at {datetime.now()}")
        db.db_entry(symbol, ltp, qntty)
    else:
        print(f"Order placement failed for {symbol}. Retrying...")

def main():
    while True:
        current_time = datetime.now().time()

        if (trade_time_morning <= current_time <= trade_stop_time_morning) or (trade_time_evening <= current_time <= trade_stop_time_evening):
            time_frame = "Morning" if trade_time_morning <= current_time <= trade_stop_time_morning else "Evening"
            print(f"\n================== {time_frame} Time =========================")

            threads = []
            for symbol in stocks.keys():
                t = threading.Thread(target=place_order_in_thread, args=(symbol,))
                threads.append(t)
                t.start()
            
            for t in threads:
                t.join()
            
            ## send report after evening execution
            if current_time > trade_time_evening:
                filepath = "Database_equity.csv"
                mail.mail_with_attachment(f" Report {current_time}", "Please find attached file as today report", filepath)
            
            # increase Target on daily basis at market open 
            if  trade_time_morning < current_time < trade_stop_time_morning:
                db.increase_target()
            break  # Exit main loop after completing one cycle for all stocks
        else:
            current_datetime = datetime.combine(datetime.today(), current_time)
            next_morning_start = datetime.combine(datetime.today(), trade_time_morning)
            next_evening_start = datetime.combine(datetime.today(), trade_time_evening)

            if current_time > trade_stop_time_evening:
                # Calculate remaining time until next morning start
                next_morning_start += timedelta(days=1)
                remaining_time = next_morning_start - current_datetime
            elif current_time > trade_stop_time_morning:
                # Calculate remaining time until next evening start
                remaining_time = next_evening_start - current_datetime
            else:
                # Calculate remaining time until next closest start time
                remaining_time = min(next_morning_start, next_evening_start) - current_datetime

            print(f"\rCurrent Time: {current_time}  || Remaining time: {remaining_time}", end="", flush=True)

        time.sleep(1)  # Wait for 1 second before checking the time again



## Program time paramater
## Time Paramaters:-
program_start_evening = datetime.strptime("13:29:00", "%H:%M:%S").time()
program_stop_evening = datetime.strptime("15:30:01", "%H:%M:%S").time()
program_start_morning = datetime.strptime("09:14:30", "%H:%M:%S").time()
program_stop_morning = datetime.strptime("09:15:15", "%H:%M:%S").time()
if __name__ == '__main__':
    while True:
        current_time = datetime.now().time()

        # Run this program twice a day (morning and evening) on weekdays (Mon-Fri)
        if (program_start_morning < current_time < program_stop_morning or program_start_evening < current_time < program_stop_evening) and is_weekday():
            if is_login():
                main()

        # Start monitoring over threading during trading hours on weekdays (Mon-Fri)
        if (trade_time_morning < current_time < trade_stop_time_morning) and is_weekday():
            if is_login():
                li_stocks = db.stock_li_to_monitor()
                for stock in li_stocks:
                    threading.Thread(target=live_monitor, args=(stock,)).start()
        else:
            for i in range(1, 4):  # Loop through 1, 2, 3
                print(f"\rTime: {current_time} | Out of Trading Time/Day {'.' * i}   ", end="", flush=True)  # The extra spaces ensure clearing
                time.sleep(1)

        time.sleep(60)


