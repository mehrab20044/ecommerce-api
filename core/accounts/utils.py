import random
import requests
import json
import redis

redis_client = redis.StrictRedis(host='redis', port=6379, db=0, decode_responses=True)

def send_otp_sms(phone_number, code):
    url = "https://api.sms.ir/v1/send/verify"
    
    api_key = "OStbdbRJyLkMXw9EO3N3gf3VlQUrQo7LKn6n190dNHrbhc2e"  
    template_id = 397164 

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "mobile": phone_number,
        "templateId": template_id,
        "parameters": [
            {
                "name": "Code",  
                "value": str(code)
            }
        ]
    }

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5)
        response_data = response.json()
        if response.status_code == 200 and response_data.get("status") == 1:
            print(f"SMS sent successfully to {phone_number}")
            return True
        else:
            print(f"SMS.ir Error: {response_data.get('message')}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"SMS Sending Failed: {e}")
        return False

def generate_and_save_otp(phone_number):
    """This function create a random code and save in redis with 2 min expiration time and send code to user phone number"""
    code = str(random.randint(1000, 9999))
    
    redis_client.setex(f"otp:{phone_number}", 120, code)
    
   
    sms_status = send_otp_sms(phone_number, code)
    return sms_status, code

def verify_otp_code(phone_number, user_code):
    """بررسی صحت کد وارد شده"""
    saved_code = redis_client.get(f"otp:{phone_number}")
    if saved_code is None:
        return "EXPIRED"
    if saved_code == str(user_code):
        redis_client.delete(f"otp:{phone_number}")
        return "VALID"
    return "INVALID"