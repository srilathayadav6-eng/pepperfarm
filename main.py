import logging
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    CallbackQueryHandler
)
from config import BOT_TOKEN

from handlers.user_handlers import start, handle_text
from handlers.payment_handlers import handle_payment_receipt
from handlers.admin_handlers import handle_admin_decision

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Please set your BOT_TOKEN in config.py")
        return

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~(filters.COMMAND), handle_text))
    application.add_handler(MessageHandler(filters.PHOTO, handle_payment_receipt))
    
    # Admin decision callbacks
    application.add_handler(CallbackQueryHandler(handle_admin_decision, pattern="^verify_"))

    print("Bot is started and polling...")
    application.run_polling()

if __name__ == '__main__':
    main()
