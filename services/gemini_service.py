import os
import google.generativeai as genai
from config import GEMINI_API_KEY
import json

if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
    genai.configure(api_key=GEMINI_API_KEY)

FAQ_DATA = [
  {
    "question": "What makes Pepperfarm different?",
    "answer": "We cook from scratch with no premixes, no preservatives, rotating menus, and balanced meals."
  },
  {
    "question": "What kind of food do you serve?",
    "answer": "We serve salads, fruit bowls, juices, soups, oats, breads, and baked items."
  },
  {
    "question": "Are your meals vegetarian?",
    "answer": "Yes, all products are 100% vegetarian. Some may contain dairy or nuts."
  },
  {
    "question": "Do you offer vegan options?",
    "answer": "Yes, many items like salads, juices, and soups are naturally vegan."
  },
  {
    "question": "Do you use preservatives?",
    "answer": "No, we do not use artificial preservatives, colours, or flavours."
  },
  {
    "question": "Which days do you deliver?",
    "answer": "We deliver on Monday, Wednesday, and Friday."
  },
  {
    "question": "Do you offer subscriptions?",
    "answer": "Yes, subscriptions are a core part of Pepperfarm."
  },
  {
    "question": "Minimum subscription?",
    "answer": "Minimum 10 deliveries."
  }
]

FAQ_CONTEXT = json.dumps(FAQ_DATA)

SYSTEM_PROMPT = f"""
You are a friendly and intelligent customer support assistant for Pepperfarm.
Your goals:
1. Help the customer first. Respond intelligently to their preferences.
2. Answer questions naturally using the FAQ.
3. Do NOT force sales. Build trust first.
4. After 1-2 interactions understanding their preference, ask gently: "Would you like me to suggest a subscription plan based on your preference?"

Tone:
- Friendly
- Natural
- Slightly conversational
- Not robotic

Rules:
- Keep answers short (2-4 lines)
- Use only information from this FAQ: {FAQ_CONTEXT}
- If unsure, say: "Our team will assist you shortly."
"""

async def get_gemini_reply(user_message: str) -> str:
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash", 
            system_instruction=SYSTEM_PROMPT
        )
        response = await model.generate_content_async(user_message)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini reply error: {e}")
        return "Our team will assist you shortly."

async def get_gemini_intent(user_message: str) -> str:
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=(
                "Classify the user's LATEST intent in the conversation into ONE of these:\n"
                "1. FAQ\n"
                "2. BUY_INTENT\n"
                "3. PAYMENT\n"
                "4. GENERAL\n\n"
                "Return ONLY the strict label.\n"
                "Return BUY_INTENT if they ask to subscribe, buy, order, purchase, or if they agree to explore subscription plans (e.g. 'yes', 'sure', 'show me plans').\n"
                "Return PAYMENT if they say they want to pay, ask for QR, or say 'OK' to proceed with payment.\n"
                "Return FAQ if they ask a question covered by company FAQ.\n"
                "Return GENERAL otherwise."
            )
        )
        response = await model.generate_content_async(user_message)
        label = response.text.strip().upper()
        
        for valid in ["FAQ", "BUY_INTENT", "PAYMENT", "GENERAL"]:
            if valid in label:
                return valid
                
        return "GENERAL"
    except Exception as e:
        print(f"Gemini intent error: {e}")
        return "GENERAL"
