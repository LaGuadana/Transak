from rate import get_quote
from auth import send_otp, verify_otp

API_KEY = ""
EMAIL = ""

quote = get_quote(
	api_key=API_KEY,
	fiat_currency="EUR",
	crypto_currency="USDC",
	fiat_amount=15000,
	payment_method="sepa_bank_transfer",
	network="stellar"
)

    # Display results
data = quote["data"]
print(f"\n💰 Quote for {data['fiatAmount']} {data['fiatCurrency']}")
print(f"You get: {data['cryptoAmount']} {data['cryptoCurrency']}")
print(f"Total fee: {data['totalFee']} {data['fiatCurrency']}")
print(f"Quote ID: {data['quoteId']}\n")
#print(f"\nFee breakdown:")
for fee in data["feeBreakdown"]:
	print(f"{fee['name']}: {fee['value']} {data['fiatCurrency']}")


print(f"Sending OTP to {EMAIL}...")
login_data = send_otp(API_KEY, EMAIL)
state_token = login_data["stateToken"]
print(f"OTP sent. State token expires in {login_data['expiresIn']}s")
	
# Step 2: User enters OTP from email
otp = input("Enter OTP from email: ").strip()
	
# Step 3: Verify and get access token
auth_data = verify_otp(API_KEY, EMAIL, otp, state_token)
access_token = auth_data["accessToken"]
	
print(f"\n✓ Authenticated!")
print(f"Access token (valid {auth_data['ttl']}s): {access_token[:40]}...")

#fastapi, postgresql