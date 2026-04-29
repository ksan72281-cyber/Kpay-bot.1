import os
import re
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

# Receipt ID များ သိမ်းဖို့ (duplicate စစ်ဖို့)
seen_ids = set()
total_amount = 0

def extract_kpay_info(text):
    """KPay ပြေစာမှ transaction ID နဲ့ ပိုက်ဆံပမာဏ ထုတ်ယူ"""
    # Transaction ID (Receipt No.)
    id_match = re.search(r'(?:Receipt No[.\s:]*|Ref(?:erence)?[.\s:]*No[.\s:]*)([A-Z0-9]+)', text, re.IGNORECASE)
    # Amount
    amount_match = re.search(r'(?:Amount|ပမာဏ)[^\d]*([\d,]+(?:\.\d+)?)', text, re.IGNORECASE)
    
    txn_id = id_match.group(1).strip() if id_match else None
    amount_str = amount_match.group(1).replace(',', '') if amount_match else None
    amount = float(amount_str) if amount_str else None
    
    return txn_id, amount

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global total_amount
    text = update.message.text or ""
    
    txn_id, amount = extract_kpay_info(text)
    
    if not txn_id or not amount:
        await update.message.reply_text("❌ KPay ပြေစာ မဟုတ်ပါ သို့မဟုတ် ဖတ်မရပါ။")
        return
    
    if txn_id in seen_ids:
        await update.message.reply_text(
            f"⚠️ ဒီပြေစာ မတင်ခင်ကတည်းက တင်ပြီးသား!\n"
            f"📋 Receipt No: {txn_id}\n"
            f"💰 စုစုပေါင်း (မပြောင်း): {total_amount:,.0f} Ks"
        )
        return
    
    seen_ids.add(txn_id)
    total_amount += amount
    
    await update.message.reply_text(
        f"✅ ထည့်သွင်းပြီး!\n"
        f"📋 Receipt No: {txn_id}\n"
        f"💵 ဒီပြေစာ: {amount:,.0f} Ks\n"
        f"💰 စုစုပေါင်း: {total_amount:,.0f} Ks"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 ပုံပြေစာများအတွက် စာသားကူးပီး ပို့ပေးပါ။")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if name == "main":
    main()
