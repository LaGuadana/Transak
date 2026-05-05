import requests
 
def get_quote(api_key, fiat_currency, crypto_currency, fiat_amount, 
              payment_method="sepa_bank_transfer", network="ethereum"):
    """Get exchange rate quote from Transak"""
    
    url = "https://api-gateway.transak.com/api/v2/lookup/quotes"
    
    params = {
        "apiKey": api_key,
        "fiatCurrency": fiat_currency,
        "cryptoCurrency": crypto_currency,
        "isBuyOrSell": "BUY",
        "network": network,
        "paymentMethod": payment_method,
        "fiatAmount": fiat_amount
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
 