from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse
import os


app = Flask(__name__)

# ✅ Environment Variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# ✅ Debugging Print to Verify Env Variables
print("✅ Loaded Environment Variables:")
print("GEMINI_API_KEY:", "Present" if GEMINI_API_KEY else "Missing ❌")
print("TWILIO_WHATSAPP_NUMBER:", TWILIO_WHATSAPP_NUMBER)

# ✅ Basic Test Route
@app.route("/", methods=["GET"])
def index():
    return "✅ Aeo-agent bot is running correctly!"

# ✅ Gemini Assistant Function
def get_gemini_response(user_input):
    print("✅ Reached Gemini API call…")  # Debugging print
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}

    aeo_persona = (
        "You are Aeo-agent, the official AI assistant of Aeologic Technologies. "
        "Always introduce yourself as Aeo-agent, reply on behalf of our team at Aeologic, "
        "and answer using our services listed on https://www.aeologic.com/. "
        "Always be professional, clear, helpful, and reference Aeologic wherever possible."
    )

    final_prompt = f"{aeo_persona}\n\nUser: {user_input}\n\nAeo-agent:"

    data = {
        "contents": [{"parts": [{"text": final_prompt}]}]
    }

    try:
        res = requests.post(url, headers=headers, params=params, json=data)
        print(f"✅ Gemini API Status Code: {res.status_code}")
        if res.status_code == 200:
            return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"❌ Gemini API failed with status code {res.status_code}"
    except Exception as e:
        print(f"❌ Error calling Gemini: {e}")
        return "❌ Error contacting Aeo-agent (Gemini API failure)."

# ✅ WhatsApp Webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "")
    print(f"✅ WhatsApp Incoming Message: {incoming_msg}")
    reply = get_gemini_response(incoming_msg)
    
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(reply)
    print(f"✅ Reply sent: {reply}")
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
