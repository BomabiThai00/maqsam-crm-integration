import requests
from config import Config

def initiate_click_to_call(agent_email, customer_phone):
    """Forces the Maqsam dialer to initiate an outbound call."""
    
    # Ensure credentials exist before trying to make the call
    if not Config.MAQSAM_ACCESS_KEY_ID or not Config.MAQSAM_ACCESS_SECRET:
        raise ValueError("Missing Maqsam API credentials in .env file.")

    url = f"https://{Config.MAQSAM_BASE_URL}/v2/calls"
    auth = (Config.MAQSAM_ACCESS_KEY_ID, Config.MAQSAM_ACCESS_SECRET)

    # Payload must be x-www-form-urlencoded
    payload = {
        "email": agent_email,
        "phone": customer_phone
    }

    try:
        response = requests.post(url, auth=auth, data=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Success: Call triggered for {customer_phone} via {agent_email}")
            return True
        elif response.status_code == 400:
            print(f"❌ Error 400: {response.json().get('message')}")
            print("Actionable: Ensure the agent is logged into the dialer (or use Autologin API).")
            return False
        else:
            print(f"⚠️ Unexpected Status {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"🚨 Network Error: {e}")
        return False

# Example execution (uncomment to test)
# initiate_click_to_call("agent@clientcrm.com", "+1234567890")