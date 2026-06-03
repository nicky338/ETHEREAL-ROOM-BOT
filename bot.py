import discord
from discord.ext import commands
import lyricsgenius
import os
import re

# --- CONFIG ---
TOKEN = os.environ.get('DISCORD_TOKEN')
GENIUS_TOKEN = os.environ.get('GENIUS_ACCESS_TOKEN')
TARGET_CHANNEL_ID = int(os.environ.get('TARGET_CHANNEL_ID', 0))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

last_played_song = ""

@bot.event
async def on_message(message):
    global last_played_song
    
    if message.author.name == "Jockie Music" and message.channel.id == TARGET_CHANNEL_ID:
        if message.embeds:
            embed = message.embeds[0]
            # Ambil semua data teks yang mungkin ada
            full_text = (embed.description or "") + " " + (embed.title or "") + " " + (embed.url or "")
            
            # --- FILTER PINTAR ---
            # Cari link YouTube di dalam teks/embed
            # Kalau ada link YouTube, bot langsung skip/return
            is_youtube_link = re.search(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)', full_text)
            
            if is_youtube_link:
                print("Link YouTube terdeteksi, skip!")
                return 

            # Cek apakah ini pesan "Started playing"
            if "started playing" in full_text.lower():
                # Ambil judul lagu
                raw = full_text.split("Started playing")[-1].strip()
                
                # Pembersih judul (Hapus [], (), dan kata "by")
                clean_title = re.sub(r'[\(\[].*?[\)\]]', '', raw).split(" by ")[0].strip()
                
                if clean_title and clean_title != last_played_song:
                    last_played_song = clean_title
                    await message.channel.send(f"Auto-Sync (Playing): {clean_title}")
                    
                    # Cari lirik di Genius
                    song = genius.search_song(clean_title)
                    if song:
                        await message.channel.send(embed=discord.Embed(title=song.title, description=song.lyrics[:2000], color=0x87CEEB))
                    else:
                        await message.channel.send("Lirik tidak ketemu.")
    
    await bot.process_commands(message)

bot.run(TOKEN)
