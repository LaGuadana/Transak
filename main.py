from transak import Transak
from store import UserStore
import secrets

API_KEY = ""
DSN = ""
WALLET = ""
EMAIL = ""

def login_or_resume(email):
    session_secret = input("Session key (blank if new/forgotten): ").strip()

    if session_secret:
        token = store.get_token(email, session_secret)
        if token is not None:
            t.access_token = token
            print(f"Resumed session for {email}")
            return
        print("Session key didn't match — re-verifying via OTP.")

    login = t.send_otp(email)
    otp = input("Enter code: ").strip()
    t.verify_otp(email, otp, login["stateToken"])
    session_secret = secrets.token_urlsafe(32)
    store.save_user(email, t.access_token, session_secret)
    print(f"Logged in {email}. Save this session key: {session_secret}")


t = Transak(api_key=API_KEY)
store = UserStore(dsn=DSN)

try:
    login_or_resume(EMAIL)
    quote = t.get_quote("EUR", "USDC", 1000)
    order = t.create_order(quote["quoteId"], WALLET, "sepa_bank_transfer")
    t.confirm_order(order["id"], "sepa_bank_transfer")
    print(f"Bought {quote['cryptoAmount']} USDC for 1000 EUR")
finally:
    store.close()
