from telegram import Update
from telegram.ext import ContextTypes
import os
from config import COMPANY_PROFILE_PDF, PAYMENT_QR_IMAGE
from services.gemini_service import get_gemini_reply, get_gemini_intent

PRODUCTS = {
    "salad": {"name": "Salad Bowl", "price": 250},
    "juice": {"name": "Cold-pressed Juice", "price": 150},
    "fruit": {"name": "Fruit Bowl", "price": 200}
}

DURATIONS = {
    "30": 30,
    "90": 90
}

# STATES
START = "START"
ASK_PRODUCT = "ASK_PRODUCT"
ASK_DURATION = "ASK_DURATION"
CONFIRM_PAYMENT = "CONFIRM_PAYMENT"
WAIT_PAYMENT = "WAIT_PAYMENT"
VERIFYING = "VERIFYING"
ASK_NAME = "ASK_NAME"
ASK_ADDRESS = "ASK_ADDRESS"
ASK_PHONE = "ASK_PHONE"
ASK_START_DATE = "ASK_START_DATE"
ASK_DIET = "ASK_DIET"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['state'] = START
    
    welcome_text = (
        "Hi! Welcome to Pepperfarm 😊\n"
        "We specialize in fresh, nutrient-rich meals like salads, juices, soups, and wholesome bakes — all made from scratch with no preservatives."
    )
    engagement_text = "Can I ask — are you looking for healthy daily meals or something occasional?"
    
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text=welcome_text)
    
    if os.path.exists(COMPANY_PROFILE_PDF):
        with open(COMPANY_PROFILE_PDF, 'rb') as pdf:
            await context.bot.send_document(chat_id=chat_id, document=pdf)
            
    await context.bot.send_message(chat_id=chat_id, text=engagement_text)
    
    context.user_data['history'] = [
        f"Bot: {welcome_text}",
        f"Bot: {engagement_text}"
    ]

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    lower_text = text.lower()
    
    if lower_text == "hi" or lower_text == "/start":
        await start(update, context)
        return
        
    state = context.user_data.get('state', START)
    
    if state == START:
        history = context.user_data.get('history', [])
        history.append(f"User: {text}")
        
        # Keep recent context
        if len(history) > 6:
            history = history[-6:]
            
        context_str = "\n".join(history)
        
        intent = await get_gemini_intent(context_str)
        reply = await get_gemini_reply(context_str)
        
        history.append(f"Bot: {reply}")
        context.user_data['history'] = history
        
        await update.message.reply_text(reply)
        
        if intent == "BUY_INTENT":
            context.user_data['state'] = ASK_PRODUCT
            await update.message.reply_text("Great! Which product are you interested in? (e.g., Salad, Juice, Fruit)")
        elif intent == "PAYMENT":
            await update.message.reply_text("Please select a product first to get your total and payment info!")
            context.user_data['state'] = ASK_PRODUCT
            await update.message.reply_text("Which product are you interested in? (e.g., Salad, Juice, Fruit)")
            
        return
        
    elif state == ASK_PRODUCT:
        selected_key = next((key for key in PRODUCTS if key in lower_text), None)
                
        if selected_key:
            context.user_data['selected_product'] = selected_key
            context.user_data['state'] = ASK_DURATION
            await update.message.reply_text("Select duration (30 / 90 days)")
        else:
            intent = await get_gemini_intent(f"User: {text}")
            reply = await get_gemini_reply(f"User: {text}")
            
            await update.message.reply_text(reply)
            
            if intent == "PAYMENT":
                await update.message.reply_text("Let's finish selecting your product first!")
                
            await update.message.reply_text("Which product are you interested in? (e.g., Salad, Juice, Fruit)")
            
    elif state == ASK_DURATION:
        if "30" in lower_text:
            dur_key = "30"
        elif "90" in lower_text:
            dur_key = "90"
        else:
            dur_key = None
            
        if dur_key:
            context.user_data['selected_duration'] = dur_key
            product_key = context.user_data['selected_product']
            total_price = PRODUCTS[product_key]['price'] * DURATIONS[dur_key]
            context.user_data['total_price'] = total_price
            
            context.user_data['state'] = CONFIRM_PAYMENT
            
            summary = (
                f"Price is Rs {total_price}.\n"
                "Type OK to proceed with payment"
            )
            await update.message.reply_text(summary)
        else:
            reply = await get_gemini_reply(f"User: {text}")
            await update.message.reply_text(reply)
            await update.message.reply_text("Now, please select duration (30 / 90 days)")
            
    elif state == CONFIRM_PAYMENT:
        if lower_text == "ok":
            context.user_data['state'] = WAIT_PAYMENT
            
            chat_id = update.effective_chat.id
            if os.path.exists(PAYMENT_QR_IMAGE):
                with open(PAYMENT_QR_IMAGE, 'rb') as img:
                    await context.bot.send_photo(chat_id=chat_id, photo=img)
            else:
                await context.bot.send_message(chat_id=chat_id, text="(QR Code Image not found locally, but it would go here.)")
                
            await update.message.reply_text("Please complete payment and upload screenshot")
        else:
            reply = await get_gemini_reply(f"User: {text}")
            await update.message.reply_text(reply)
            await update.message.reply_text("Type OK to proceed with payment.")
            
    elif state == WAIT_PAYMENT:
        reply = await get_gemini_reply(f"User: {text}")
        await update.message.reply_text(reply)
        await update.message.reply_text("Please upload an image screenshot of your payment receipt to proceed.")
        
    elif state == VERIFYING:
        reply = await get_gemini_reply(f"User: {text}")
        await update.message.reply_text(reply)
        await update.message.reply_text("Payment under verification. Please wait for the admin to approve.")
        
    elif state == ASK_NAME:
        context.user_data['full_name'] = text
        context.user_data['state'] = ASK_ADDRESS
        await update.message.reply_text("Thank you! Please provide your Delivery Address:")
        
    elif state == ASK_ADDRESS:
        context.user_data['address'] = text
        context.user_data['state'] = ASK_PHONE
        await update.message.reply_text("Got it. Please provide your Phone Number:")
        
    elif state == ASK_PHONE:
        context.user_data['phone'] = text
        context.user_data['state'] = ASK_START_DATE
        await update.message.reply_text("Thank you. What is your Preferred Start Date?")
        
    elif state == ASK_START_DATE:
        context.user_data['start_date'] = text
        context.user_data['state'] = ASK_DIET
        await update.message.reply_text("Almost done! Any dietary preferences we should know about? (You can type 'None' if not applicable)")
        
    elif state == ASK_DIET:
        context.user_data['diet'] = text
        
        from services.storage_service import StorageService
        storage = StorageService()
        
        telegram_id = update.effective_user.id
        full_name = context.user_data.get('full_name', 'Unknown')
        address = context.user_data.get('address', 'Unknown')
        phone = context.user_data.get('phone', 'Unknown')
        start_date = context.user_data.get('start_date', 'Unknown')
        diet = context.user_data.get('diet', 'None')
        
        product_key = context.user_data.get('selected_product')
        duration_key = context.user_data.get('selected_duration')
        total_price = context.user_data.get('total_price')
        
        if product_key and duration_key:
            product_name = PRODUCTS[product_key]['name']
            duration_val = f"{DURATIONS[duration_key]} days"
        else:
            product_name = "Unknown"
            duration_val = "Unknown"
        
        try:
            storage.add_subscription(
                telegram_id=telegram_id,
                full_name=full_name,
                address=address,
                phone=phone,
                start_date=start_date,
                diet=diet,
                product=product_name,
                duration=duration_val,
                price=total_price,
                status="Onboarded"
            )
            
            context.user_data['state'] = START
            
            final_msg = (
                "🎉 Onboarding complete! All your details have been saved successfully.\n\n"
                "We are thrilled to embark on this healthy journey with you! "
                "Our team will reach out to you shortly before your first delivery."
            )
            await update.message.reply_text(final_msg)
        except PermissionError:
            await update.message.reply_text("⚠️ Oops! Your details couldn't be saved because the `data.xlsx` file is currently open on our server. Please ask the admin to close it, and then type your dietary preference again to re-submit!")
        except Exception as e:
            print(f"Error saving to Excel: {e}")
            await update.message.reply_text("⚠️ An error occurred while saving your details. Please try typing your dietary preference again.")
