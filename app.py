from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

# Load credentials from Railway environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

def get_gemini_response(user_input):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    data = {
        "contents": [{"parts": [{"text": user_input}]}]
    }

    res = requests.post(url, headers=headers, params=params, json=data)
    if res.status_code == 200:
        try:
            return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        except:
            return "Gemini gave an unexpected response."
    else:
        return "Failed to connect to Gemini."

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "")
    print(f"User said: {incoming_msg}")
    reply = get_gemini_response(incoming_msg)

    # Reply via WhatsApp
    twilio_resp = MessagingResponse()
    msg = twilio_resp.message()
    msg.body(reply)
    return str(twilio_resp)

if __name__ == "__main__":
    app.run(debug=True)
