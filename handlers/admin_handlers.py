from telegram import Update
from telegram.ext import ContextTypes

async def handle_admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')
    decision = data[1] # 'approve' or 'reject'
    user_id = int(data[2])
    
    # Access user's state data
    user_data = context.application.user_data.get(user_id, {})
    
    if decision == "approve":
        status = "Approved"
        user_message = "✅ Payment verified. Welcome to Pepperfarm!\n\nPlease tell us your Full Name:"
        
        # Setup onboarding state
        user_data['state'] = "ASK_NAME"
    else:
        status = "Rejected"
        user_message = "❌ Sorry, we could not verify your payment. Please re-upload your payment proof."
        user_data['state'] = "WAIT_PAYMENT"
        
    # Notify User
    try:
        await context.bot.send_message(chat_id=user_id, text=user_message)
    except Exception as e:
        print(f"Could not notify user {user_id}: {e}")
        
    # Update Admin Message
    current_caption = query.message.caption if query.message.caption else "Payment Verification"
    new_caption = f"{current_caption}\n\n[Status: {status} by Admin]"
    await query.edit_message_caption(caption=new_caption)
