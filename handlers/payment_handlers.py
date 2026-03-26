from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ADMIN_ID
from handlers.user_handlers import PRODUCTS, DURATIONS, WAIT_PAYMENT, VERIFYING

async def handle_payment_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state')
    
    if state != WAIT_PAYMENT:
        await update.message.reply_text("I'm not expecting a photo right now. Type 'Hi' to start.")
        return
        
    user = update.effective_user
    photo_file = update.message.photo[-1] # Highest resolution photo
    
    product_key = context.user_data.get('selected_product')
    duration_key = context.user_data.get('selected_duration')
    total_price = context.user_data.get('total_price')
    
    if not product_key or not duration_key:
        await update.message.reply_text("Something went wrong. Please start again by typing 'Hi'.")
        context.user_data['state'] = "START"
        return
        
    product_name = PRODUCTS[product_key]['name']
    duration = DURATIONS[duration_key]
    
    # Save user details to use in admin handler
    context.user_data['user_first_name'] = user.first_name
    
    context.user_data['state'] = VERIFYING
    await update.message.reply_text("Payment under verification")
    
    # Forward to Admin
    caption = (
        f"🆕 New Subscription Payment!\n\n"
        f"User: {user.first_name} (@{user.username})\n"
        f"Telegram ID: {user.id}\n"
        f"Product: {product_name}\n"
        f"Duration: {duration} days\n"
        f"Total Price: Rs {total_price}\n"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("Approve", callback_data=f"verify_approve_{user.id}"),
            InlineKeyboardButton("Reject", callback_data=f"verify_reject_{user.id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        if ADMIN_ID and ADMIN_ID != "YOUR_ADMIN_ID_HERE":
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo_file.file_id,
                caption=caption,
                reply_markup=reply_markup
            )
        else:
            print(f"Would have sent to admin {ADMIN_ID}: {caption}")
    except Exception as e:
        print(f"Failed to send to admin: {e}")
