import requests


BASE_URL = "https://api-gateway-stg.transak.com"

class Transak:
    def __init__(self, api_key):
        self.api_key = api_key
        self.access_token = None

    def get_quote(self, fiat_currency, crypto_currency,fiat_amount, 
              payment_method="sepa_bank_transfer", network="ethereum"):
        params = {
            "apiKey": self.api_key,
            "fiatCurrency": fiat_currency,
            "cryptoCurrency": crypto_currency,
            "isBuyOrSell": "BUY",
            "network": network,
            "paymentMethod": payment_method,
            "fiatAmount": fiat_amount
        }
        
        response = requests.get(f"{BASE_URL}/api/v2/lookup/quotes", params=params)
        response.raise_for_status()
        return response.json()["data"]
    
    def send_otp(self, email):
        payload = {"apiKey": self.api_key, "email": email}
        response = requests.post(f"{BASE_URL}/api/v2/auth/login", json=payload)
        response.raise_for_status()
        return response.json()["data"]
    
    def verify_otp(self, email, otp, state_token):
        payload = {
            "apiKey": self.api_key,
            "email": email,
            "otp": otp,
            "stateToken": state_token
        }
        
        response = requests.post(f"{BASE_URL}/api/v2/auth/verify", json=payload)
        response.raise_for_status()
        data = response.json()["data"]
        self.access_token = data["accessToken"]
        return data
    
    def create_order(self, quote_id, wallet_address, payment_method):
        if self.access_token is None:
            raise RuntimeError("Not logged in, use verify_otp method first")
        headers = {"authorization": self.access_token}
        payload = {
            "quoteId": quote_id,
            "paymentInstrumentId": payment_method,
            "walletAddress": wallet_address,
        }
        
        response = requests.post(f"{BASE_URL}/api/v2/orders", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["data"]
     

 
    def confirm_order(self, order_id, payment_method):
        headers = {"authorization" : self.access_token}
        payload = {
            "orderId" : order_id,
            "paymentMethod" : payment_method
        }

        response = requests.post(f"{BASE_URL}/api/v2/orders/payment-confirmation", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["data"]








