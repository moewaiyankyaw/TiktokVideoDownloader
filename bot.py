import requests
import re
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from io import BytesIO
from flask import Flask, jsonify
import threading
import time

# Disable all logging
logging.disable(logging.CRITICAL)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Your Telegram Bot Token
BOT_TOKEN = os.environ.get('BOT_TOKEN', "8402815013:AAFr3DwTxkN6B2w90KMKBAaVETCCjns0hgM")

# TikTok URL pattern for detection
TIKTOK_URL_PATTERN = r'https?://(?:vm|vt|www)\.tiktok\.com/\S+|https?://tiktok\.com/\S+'

# Burmese language messages
BURMESE_MESSAGES = {
    "welcome": "ဟယ်လို! ကျွန်တော်က TikTok ဗီဒီယိုဒေါင်း�လုဒ်ဆွဲပေးတဲ့ bot ပါ။",
    "help": (
        "ဒီ bot ကိုဘယ်လိုသုံးမလဲ:\n\n"
        "1. ကျွန်တော့်ကို TikTok link တစ်ခုပေးပါ\n"
        "2. ဒါမှမဟုတ် group ထဲထည့်ပြီး TikTok link တွေကိုအလိုအလျောက်လုပ်ပေးမယ်\n\n"
        "ကျွန်တော်က TikTok watermark မပါတဲ့ဗီဒီယိုကိုဒေါင်း�လုဒ်ဆွဲပေးပါမယ်!"
    ),
    "processing": "🔄 TikTok ဗီဒီယိုကိုလုပ်ဆောင်နေပါတယ်...",
    "success": "✅ ဗီဒီယိုအောင်မြင်စွာဒေါင်းလုဒ်ဆွဲပြီးပါပြီ!",
    "error": "❌ ဗီဒီယိုဒေါင်းလုဒ်ဆွဲရန်မအောင်မြင်ပါ။ link မှားယွင်း�နေနိုင်သည် သို့မဟုတ် service ခဏလုံးပျက်�နေနိုင်သည်။",
    "caption": "ဒါကတော့ TikTok watermark မပါတဲ့ဗီဒီယိုပါ!",
    "api_error": "❌ ဗီဒီယိုဒေါင်းလုဒ်ဆွဲရန်မအောင်မြင်ပါ။ API ပြဿနာရှိနေနိုင်သည်။",
    "general_error": "❌ ဗီဒီယိုလုပ်ဆောင်�ရာတွင်အမှားတစ်ခုဖြစ်ပွားခဲ့သည်။",
    "developer": "Bot Developer - @M69431",
    "commands_title": "📋 Available Commands:",
    "how_to_use": "📖 How to Use",
    "support": "💬 Support",
    "download_example": "⬇️ Download Example"
}

# Flask app for health checks
app = Flask(__name__)

@app.route('/')
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "TikTok Downloader Bot (Burmese)",
        "language": "myanmar",
        "developer": "@M69431",
        "timestamp": time.time()
    })

@app.route('/health')
def health():
    return jsonify({"status": "ok", "language": "burmese"})

@app.route('/language')
def language_info():
    return jsonify({
        "language": "burmese",
        "developer": "@M69431"
    })

@app.route('/developer')
def developer_info():
    return jsonify({
        "developer": "@M69431",
        "bot": "TikTok Video Downloader",
        "language": "Burmese"
    })

def run_flask():
    """Run Flask server for health checks"""
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def get_welcome_keyboard():
    """Create inline keyboard for welcome message"""
    keyboard = [
        [InlineKeyboardButton(BURMESE_MESSAGES["how_to_use"], callback_data="help")],
        [InlineKeyboardButton(BURMESE_MESSAGES["support"], url="https://t.me/M69431")],
        [InlineKeyboardButton(BURMESE_MESSAGES["download_example"], callback_data="example")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_text = f"""
{BURMESE_MESSAGES['welcome']}

{BURMESE_MESSAGES['commands_title']}
• /start - Bot ကိုစတင်ရန်
• /help - အကူအညီရယူရန်
• /developer - Developer နှင့်ချိတ်ဆက်ရန်

{BURMESE_MESSAGES['developer']}
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_welcome_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = f"""
{BURMESE_MESSAGES['help']}

📝 သုံးစွဲနည်း:
1. TikTok video link ကိုကူးယူပါ
2. ဒီ bot ကိုပို့ပေးပါ
3. Watermark မပါတဲ့ video ကိုရယူပါ

{BURMESE_MESSAGES['developer']}
    """
    
    keyboard = [
        [InlineKeyboardButton("💬 Developer နှင့်ဆက်သွယ်ရန်", url="https://t.me/M69431")],
        [InlineKeyboardButton("⬅️ Back to Start", callback_data="start")]
    ]
    
    await update.message.reply_text(
        help_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def developer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show developer information."""
    developer_text = f"""
👨‍💻 Bot Developer Information:

{BURMESE_MESSAGES['developer']}

📧 Telegram: @M69431
🤖 This bot: @{(await context.bot.get_me()).username}

💡 Features:
• TikTok video download without watermark
• Fast and reliable
• Burmese language support
• Free to use
    """
    
    keyboard = [
        [InlineKeyboardButton("📩 Contact Developer", url="https://t.me/M69431")],
        [InlineKeyboardButton("⭐ Rate This Bot", callback_data="rate")],
        [InlineKeyboardButton("⬅️ Back to Start", callback_data="start")]
    ]
    
    await update.message.reply_text(
        developer_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "help":
        await help_command_callback(query)
    elif query.data == "start":
        await start_command_callback(query)
    elif query.data == "example":
        await example_callback(query)
    elif query.data == "rate":
        await query.message.reply_text("⭐ Thank you for using this bot!")

async def help_command_callback(query):
    """Handle help button callback"""
    help_text = f"""
{BURMESE_MESSAGES['help']}

📝 သုံးစွဲနည်း:
1. TikTok video link ကိုကူးယူပါ
2. ဒီ bot ကိုပို့ပေးပါ
3. Watermark မပါတဲ့ video ကိုရယူပါ

{BURMESE_MESSAGES['developer']}
    """
    
    keyboard = [
        [InlineKeyboardButton("💬 Developer နှင့်ဆက်သွယ်ရန်", url="https://t.me/M69431")],
        [InlineKeyboardButton("⬅️ Back to Start", callback_data="start")]
    ]
    
    await query.edit_message_text(
        help_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start_command_callback(query):
    """Handle start button callback"""
    welcome_text = f"""
{BURMESE_MESSAGES['welcome']}

{BURMESE_MESSAGES['commands_title']}
• /start - Bot ကိုစတင်ရန်
• /help - အကူအညီရယူရန်
• /developer - Developer နှင့်ချိတ်ဆက်ရန်

{BURMESE_MESSAGES['developer']}
    """
    
    await query.edit_message_text(
        welcome_text,
        reply_markup=get_welcome_keyboard()
    )

async def example_callback(query):
    """Handle example button callback"""
    example_text = """
📥 Download Example:

ဒီလို TikTok link တစ်ခုပို့ပေးပါ:
https://vt.tiktok.com/ZSAy3rPhy/

ဒါမှမဟုတ်:
https://www.tiktok.com/@username/video/1234567890

ကျွန်တော်က watermark မပါတဲ့ video ကိုဒေါင်းလုဒ်ဆွဲပေးပါမယ်!
    """
    
    keyboard = [
        [InlineKeyboardButton("📖 Full Guide", callback_data="help")],
        [InlineKeyboardButton("💬 Support", url="https://t.me/M69431")],
        [InlineKeyboardButton("⬅️ Back to Start", callback_data="start")]
    ]
    
    await query.edit_message_text(
        example_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def extract_tiktok_urls(text):
    """Extract TikTok URLs from text"""
    return re.findall(TIKTOK_URL_PATTERN, text)

def download_tiktok_no_watermark(url):
    """
    Download TikTok video without watermark using tikwm API
    Returns video data as bytes or None if failed
    """
    try:
        # First, resolve the short URL to get the full TikTok URL
        if "vt.tiktok.com" in url or "vm.tiktok.com" in url:
            response = requests.head(url, allow_redirects=True, timeout=10)
            full_url = response.url
        else:
            full_url = url

        # Extract video ID
        video_id_match = re.search(r'/video/(\d+)', full_url)
        if not video_id_match:
            return None
        
        video_id = video_id_match.group(1)
        
        # Use tikwm API
        tikwm_api = f"https://tikwm.com/api/?url={full_url}&hd=1"
        
        # Add proper headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Origin': 'https://tikwm.com',
            'Referer': 'https://tikwm.com/',
        }
        
        response = requests.get(tikwm_api, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0 and 'data' in data:
                download_url = data['data']['play']
                
                # Download the video with headers
                video_response = requests.get(download_url, headers=headers, timeout=30)
                
                if video_response.status_code == 200:
                    return video_response.content
        
        return None
            
    except Exception:
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and check for TikTok URLs."""
    # Check if the message contains a TikTok URL
    message_text = update.message.text or update.message.caption or ""
    tiktok_urls = extract_tiktok_urls(message_text)
    
    if not tiktok_urls:
        return
    
    # Process each TikTok URL found
    for url in tiktok_urls:
        # Send a "processing" message in Burmese
        processing_msg = await update.message.reply_text(BURMESE_MESSAGES["processing"])
        
        try:
            # Download the video without watermark
            video_data = download_tiktok_no_watermark(url)
            
            if video_data:
                # Create a file-like object from the video data
                video_file = BytesIO(video_data)
                video_file.name = "tiktok_no_watermark.mp4"
                
                # Send the video back to the user with Burmese caption
                await update.message.reply_video(
                    video=video_file,
                    caption=f"{BURMESE_MESSAGES['caption']}\n\n{BURMESE_MESSAGES['developer']}",
                    supports_streaming=True
                )
                
                # Edit the processing message to indicate success in Burmese
                await processing_msg.edit_text(BURMESE_MESSAGES["success"])
            else:
                await processing_msg.edit_text(BURMESE_MESSAGES["api_error"])
                
        except Exception:
            await processing_msg.edit_text(BURMESE_MESSAGES["general_error"])

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Silent error handler - no logging"""
    pass

def main():
    """Start the bot and web server."""
    # Start Flask server in a separate thread for health checks
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("developer", developer_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)

    # Start the Bot silently
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
        read_timeout=30,
        write_timeout=30,
        connect_timeout=30,
        pool_timeout=30
    )

if __name__ == "__main__":
    main()
