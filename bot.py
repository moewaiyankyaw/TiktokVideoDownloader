import requests
import re
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from io import BytesIO
from flask import Flask, jsonify
import threading
import time

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your Telegram Bot Token
BOT_TOKEN = os.environ.get('BOT_TOKEN', "8402815013:AAFr3DwTxkN6B2w90KMKBAaVETCCjns0hgM")

# TikTok URL pattern for detection
TIKTOK_URL_PATTERN = r'https?://(?:vm|vt|www)\.tiktok\.com/\S+|https?://tiktok\.com/\S+'

# Burmese language messages
BURMESE_MESSAGES = {
    "welcome": "ဟယ်လို! ကျွန်တော်က TikTok ဗီဒီယိုဒေါင်းလုဒ်ဆွဲပေးတဲ့ bot ပါ။",
    "help": (
        "ဒီ bot ကိုဘယ်လိုသုံးမလဲ:\n\n"
        "1. ကျွန်တော့်ကို TikTok link တစ်ခုပေးပါ\n"
        "2. ဒါမှမဟုတ် group ထဲထည့်ပြီး TikTok link တွေကိုအလိုအလျောက်လုပ်ပေးမယ်\n\n"
        "ကျွန်တော်က TikTok watermark မပါတဲ့ဗီဒီယိုကိုဒေါင်းလုဒ်ဆွဲပေးပါမယ်!"
    ),
    "processing": "🔄 TikTok ဗီဒီယိုကိုလုပ်ဆောင်နေပါတယ်...",
    "success": "✅ ဗီဒီယိုအောင်မြင်စွာဒေါင်းလုဒ်ဆွဲပြီးပါပြီ!",
    "error": "❌ ဗီဒီယိုဒေါင်းလုဒ်ဆွဲရန်မအောင်မြင်ပါ။ link မှားယွင်းနေနိုင်သည် သို့မဟုတ် service ခဏလုံးပျက်နေနိုင်သည်။",
    "caption": "ဒါကတော့ TikTok watermark မပါတဲ့ဗီဒီယိုပါ! \n\n (ယခု Bot ကို ဖန်တီးပေးထားသူမှာ - @M69431 ဖြစ်ပါသည်)",
    "api_error": "❌ ဗီဒီယိုဒေါင်းလုဒ်ဆွဲရန်မအောင်မြင်ပါ။ API ပြဿနာရှိနေနိုင်သည်။",
    "general_error": "❌ ဗီဒီယိုလုပ်ဆောင်ရာတွင်အမှားတစ်ခုဖြစ်ပွားခဲ့သည်။"
}

# Flask app for health checks
app = Flask(__name__)

@app.route('/')
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "TikTok Downloader Bot (Burmese)",
        "language": "myanmar",
        "timestamp": time.time()
    })

@app.route('/health')
def health():
    return jsonify({"status": "ok", "language": "burmese"})

@app.route('/language')
def language_info():
    return jsonify({
        "language": "burmese",
        "messages": list(BURMESE_MESSAGES.keys())
    })

def run_flask():
    """Run Flask server for health checks"""
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(BURMESE_MESSAGES["welcome"])

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(BURMESE_MESSAGES["help"])

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show language information."""
    await update.message.reply_text("ဒီ bot က မြန်မာဘာသာစကားကိုသုံးထားပါတယ်။")

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
        
        logger.info(f"Resolved URL: {full_url}")
        
        # Extract video ID
        video_id_match = re.search(r'/video/(\d+)', full_url)
        if not video_id_match:
            logger.error("Could not extract video ID from URL")
            return None
        
        video_id = video_id_match.group(1)
        logger.info(f"Video ID: {video_id}")
        
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
        
        logger.error("Download failed. The API might be down or blocked.")
        return None
            
    except Exception as e:
        logger.error(f"Error in download_tiktok_no_watermark: {str(e)}")
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
                    caption=BURMESE_MESSAGES["caption"],
                    supports_streaming=True
                )
                
                # Edit the processing message to indicate success in Burmese
                await processing_msg.edit_text(BURMESE_MESSAGES["success"])
            else:
                await processing_msg.edit_text(BURMESE_MESSAGES["api_error"])
                
        except Exception as e:
            logger.error(f"Error processing TikTok video: {e}")
            await processing_msg.edit_text(BURMESE_MESSAGES["general_error"])

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by Updates."""
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    """Start the bot and web server."""
    # Start Flask server in a separate thread for health checks
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    logger.info("Starting Telegram Bot (Burmese)...")
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    # Start the Bot
    logger.info("Bot is starting in Burmese language...")
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()
