import time
import hashlib
import hmac
import requests

API_KEY = "DEV-42dSinWzhyuBk8XOBY3DbHy02K07MO4lmp4XLtIl"
PRIVATE_KEY = "ystcc-dOYq7-BFL2z-DLYz3-up1Lm"
MERCHANT_CODE = "T14876"
TRIPAY_URL = "https://tripay.co.id/api-sandbox/transaction/create"


def request_tripay_payment(method, merchant_ref, amount, customer_name, customer_email, customer_phone, product_sku, product_name):
    
    signature = hmac.new(
        PRIVATE_KEY.encode(),
        f"{MERCHANT_CODE}{merchant_ref}{amount}".encode(),
        hashlib.sha256
    ).hexdigest()

    payload = {
        "method": method,
        "merchant_ref": merchant_ref,
        "amount": amount,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "customer_phone": customer_phone,
        "order_items": [
            {
                "sku": product_sku,
                "name": product_name,
                "price": amount,
                "quantity": 1,
                "product_url": "-",
                "image_url": "-"
            }
        ],
        "signature": signature
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(TRIPAY_URL, headers=headers, json=payload)

    try:
        return response.json()
    except:
        return {"success": False, "message": "Invalid JSON from Tripay"}
