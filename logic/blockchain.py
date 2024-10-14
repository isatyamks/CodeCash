import requests

def get_bitcoin_price_in_inr():
   
   #api fetched
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=inr"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('bitcoin', {}).get('inr')
    
    
    
    
    except requests.exceptions.RequestException as e:
        print(f"problem fetching the Bitcoin price: {e}")
        return None


def convert_inr_to_bitcoin(inr_amount):
    bitcoin_price_in_inr = get_bitcoin_price_in_inr()
    
    if bitcoin_price_in_inr:
        bitcoin_amount = inr_amount / bitcoin_price_in_inr
        return bitcoin_amount
    else:
        return None

if __name__ == "__main__":
    
    try:
        inr_amount = int(input("enter the amount: "))
        bitcoin_amount = convert_inr_to_bitcoin(inr_amount)
        
        if bitcoin_amount is not None:
            print(f"₹{inr_amount} is equivalent to {bitcoin_amount:.8f} BTC.")
        else:
            print("here is a api fetching error")
    except ValueError:
        print("here is a value error")
