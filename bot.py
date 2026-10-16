import os
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import yt_dlp

API_ID = "YOUR_API_ID"
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "YOUR_BOT_TOKEN"

app = Client("jiohotstar_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ഡൗൺലോഡ് പ്രോഗ്രസ്സ് ടെലഗ്രാമിൽ അപ്ഡേറ്റ് ചെയ്യാൻ
def get_progress_hook(client, message):
    last_update_time = 0
    def progress_hook(d):
        nonlocal last_update_time
        if d['status'] == 'downloading':
            current_time = time.time()
            # സ്പാമിങ് ഒഴിവാക്കാൻ 3 സെക്കൻഡിൽ ഒരിക്കൽ മാത്രം മെസ്സേജ് അപ്ഡേറ്റ് ചെയ്യുക
            if current_time - last_update_time > 3:
                percentage = d.get('_percent_str', '0%').strip()
                speed = d.get('_speed_str', 'N/A').strip()
                eta = d.get('_eta_str', 'N/A').strip()
                try:
                    client.loop.create_task(
                        message.edit_text(
                            f"📥 ഡൗൺലോഡ് പുരോഗമിക്കുന്നു...\n\n"
                            f"📊 ശതമാനം: {percentage}\n"
                            f"🚀 വേഗത: {speed}\n"
                            f"⏱️ ബാക്കി സമയം: {eta}"
                        )
                    )
                except Exception:
                    pass
                last_update_time = current_time
    return progress_hook

@app.on_message(filters.text & filters.private)
async def get_link(client, message):
    url = message.text.strip()
    
    if "hotstar.com" in url:
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("1080p", callback_data=f"dl|1080|{url}"),
                InlineKeyboardButton("720p", callback_data=f"dl|720|{url}")
            ],
            [
                InlineKeyboardButton("480p", callback_data=f"dl|480|{url}"),
                InlineKeyboardButton("360p", callback_data=f"dl|360|{url}")
            ]
        ])
        await message.reply_text("ദയവായി ആവശ്യമായ ക്വാളിറ്റി തെരഞ്ഞെടുക്കുക:", reply_markup=keyboard)
    else:
        await message.reply_text("ദയവായി ശരിയായ ജിയോ ഹോസ്റ്റാർ ലിങ്ക് അയക്കുക.")

@app.on_callback_query(filters.regex("^dl\\|"))
async def download_video(client, callback_query: CallbackQuery):
    data_parts = callback_query.data.split("|")
    quality = data_parts[1]
    url = data_parts[2]
    
    status_msg = await callback_query.message.edit_text(f" തിരഞ്ഞെടുക്കപ്പെട്ട ക്വാളിറ്റി: {quality}p. ഡൗൺലോഡ് ആരംഭിക്കുന്നു...")

    ydl_opts = {
        'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best',
        'cookiefile': 'cookies.txt',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'progress_hooks': [get_progress_hook(client, status_msg)],
    }

    try:
        os.makedirs("downloads", exist_ok=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await status_msg.edit_text(" വീഡിയോ അപ്‌ലോഡ് ചെയ്യുന്നു...")
        await client.send_video(
            chat_id=callback_query.message.chat.id,
            video=filename,
            caption=f" ഇവിടെ നിങ്ങളുടെ ജിയോ ഹോസ്റ്റാർ വീഡിയോ ({quality}p)!"
        )
        
        await status_msg.delete()
        
        if os.path.exists(filename):
            os.remove(filename)
            
    except Exception as e:
        await status_msg.edit_text(f"ഡൗൺലോഡ് ചെയ്യുന്നതിൽ പരാജയപ്പെട്ടു: {str(e)}")

if __name__ == "__main__":
    print("ബോട്ട് റൺ ആകുന്നു...")
    app.run()
