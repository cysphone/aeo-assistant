from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

# Env Variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# Function to get Gemini Response
def get_gemini_response(user_input):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}

    # Aeo-agent Persona Prompt
    aeo_persona = (
        "You are Aeo-agent, the official AI assistant of Aeologic Technologies. "
        "Always introduce yourself as Aeo-agent and respond on behalf of our team at Aeologic. "
        "Your responses must reflect our services, solutions, and industry knowledge. "
        "Use 'we', 'our team', and 'at Aeologic' throughout your responses. "
        "Prioritize information from https://www.aeologic.com/ "
        "Be helpful, professional, clear, and direct."
    )

    final_prompt = f"{aeo_persona}\n\nUser: {user_input}\n\nAeo-agent:"

    data = {
        "contents": [{"parts": [{"text": final_prompt}]}]
    }

    res = requests.post(url, headers=headers, params=params, json=data)

    if res.status_code == 200:
        try:
            return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        except:
            return "Gemini returned a response I couldn't process."
    else:
        return f"Error fetching response from Gemini: {res.status_code}"

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "")
    print(f"Incoming WhatsApp message: {incoming_msg}")
    reply = get_gemini_response(incoming_msg)

    resp = MessagingResponse()
    msg = resp.message()
    msg.body(reply)
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

