from flask import Flask, request, jsonify
import hmac
import hashlib
from db import get_connection  

app = Flask(__name__)

PRIVATE_KEY = "ystcc-dOYq7-BFL2z-DLYz3-up1Lm"


@app.route('/tripay-callback', methods=['POST'])
def tripay_callback():

    raw_body = request.data.decode('utf-8')

    # Signature
    calculated_signature = hmac.new(
        PRIVATE_KEY.encode(),
        raw_body.encode(),
        hashlib.sha256
    ).hexdigest()

    # Signature dari Tripay
    incoming_signature = request.headers.get("X-Callback-Signature")

    if calculated_signature != incoming_signature:
        return jsonify({"success": False, "message": "Invalid signature"}), 403

    data = request.get_json()

    print("Callback Diterima:", data)

    reference = data.get("reference")
    tripay_status = data.get("status")  # PAID / UNPAID / EXPIRED

    # Mapping status
    status_map = {
        "PAID": "success",
        "UNPAID": "pending",
        "EXPIRED": "expired"
    }

    final_status = status_map.get(tripay_status, "pending")

    # Update ke database
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "UPDATE transactions SET status=%s WHERE reference=%s"
        cursor.execute(sql, (final_status, reference))
        conn.commit()

        print(f"Status transaksi {reference} diperbarui menjadi: {final_status}")

    except Exception as e:
        print("DB Error:", e)
        return jsonify({"success": False}), 500

    return jsonify({"success": True})
    

if __name__ == '__main__':
    app.run(port=5000)
