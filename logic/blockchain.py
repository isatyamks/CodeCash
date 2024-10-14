import requests

def get_bitcoin_price_in_inr():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=inr"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('bitcoin', {}).get('inr')
    except requests.exceptions.RequestException as e:
        print(f"Oops! There was a problem fetching the Bitcoin price: {e}")
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
        inr_amount = int(input("Please enter the amount in Indian Rupees (INR) that you wish to convert to Bitcoin: "))
        bitcoin_amount = convert_inr_to_bitcoin(inr_amount)
        
        if bitcoin_amount is not None:
            print(f"Great! ₹{inr_amount} is equivalent to {bitcoin_amount:.8f} BTC.")
        else:
            print("Unfortunately, we couldn't complete the conversion. Please try again later.")
    except ValueError:
        print("Hmm, it seems like you entered something that isn't a valid number. Please try again with a whole number for INR.")
