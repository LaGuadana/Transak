import requests

BASE_URL = "https://api-gateway-stg.transak.com"


def send_otp(api_key, email):
	url = f"{BASE_URL}/api/v2/auth/login"
	payload = {"apiKey": api_key, "email": email}
	
	response = requests.post(url, json=payload)
	response.raise_for_status()
	return response.json()["data"]


def verify_otp(api_key, email, otp, state_token):
	"""Verify OTP and get access token (valid 30 days)."""
	url = f"{BASE_URL}/api/v2/auth/verify"
	payload = {
		"apiKey": api_key,
		"email": email,
		"otp": otp,
		"stateToken": state_token
	}
	
	response = requests.post(url, json=payload)
	response.raise_for_status()
	return response.json()["data"]
