import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PORN_PEN_API_KEY = os.getenv("PORN_PEN_API_KEY")
BOT_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

app = Flask(__name__)

def send_message(chat_id, text):
    requests.post(f"{BOT_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def send_photo(chat_id, photo_url):
    requests.post(f"{BOT_URL}/sendPhoto", json={
        "chat_id": chat_id,
        "photo": photo_url
    })

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.startswith("/image"):
            prompt = text.replace("/image", "").strip()
            if not prompt:
                send_message(chat_id, "Please provide a prompt. Example:\n/image redhead elf with big boobs")
                return "ok"

            send_message(chat_id, "🖌 Generating your image... please wait.")

            # Call Pornpen API
            try:
                headers = {
                    "Authorization": f"Bearer {PORN_PEN_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "prompt": prompt,
                    "nsfw": True,
                    "num_images": 1,
                    "resolution": "512x768"
                }
                response = requests.post("https://api.pornpen.ai/generate", headers=headers, json=payload)
                result = response.json()

                if response.status_code == 200 and result.get("images"):
                    image_url = result["images"][0]["url"]
                    send_photo(chat_id, image_url)
                else:
                    send_message(chat_id, "❌ Failed to generate image. Try again later.")
            except Exception as e:
                send_message(chat_id, f"❌ Error: {str(e)}")

    return "ok"
