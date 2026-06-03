import discord
from discord.ext import commands
import lyricsgenius
import os
import re

# --- CONFIG ---
TOKEN = os.environ.get('DISCORD_TOKEN')
GENIUS_TOKEN = os.environ.get('GENIUS_ACCESS_TOKEN')
TARGET_CHANNEL_ID = int(os.environ.get('TARGET_CHANNEL_ID', 0))

# Setup Intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

last_played_song = ""

@bot.event
async def on_ready():
    print(f'Bot Ethereal sudah ON dan siap beraksi secara Instan!')

@bot.event
async def on_message(message):
    global last_played_song
    
    # Filter channel dan author
    if message.author.name == "Jockie Music" and message.channel.id == TARGET_CHANNEL_ID:
        if message.embeds:
            embed = message.embeds[0]
            # Gabungin semua teks embed buat dideteksi
            full_text = (embed.description or "") + " " + (embed.title or "") + " " + " ".join([f.value for f in embed.fields])
            
            if "Started playing" in full_text:
                # 1. FILTER CERDAS: Cek teks, bukan cuma link
                # Kalau ada kata "YouTube" atau kata-kata playlist, langsung skip
                is_youtube_content = "youtube" in full_text.lower()
                is_playlist = any(keyword.lower() in full_text.lower() for keyword in ["Full Album", "Playlist", "Album", "Lagu Pop"])
                
                if is_youtube_content or is_playlist:
                    print("Konten YouTube atau Playlist terdeteksi, skip lirik.")
                    return # Berhenti, nggak usah cari lirik!

                # 2. PROSES LANJUT (Cuma kalau lolos filter)
                raw = full_text.split("Started playing")[-1].strip()
                title = re.sub(r'\(.*?\)', '', raw).split(" by ")[0].strip()
                
                if title != last_played_song:
                    last_played_song = title
                    await message.channel.send(f"Auto-Sync (Playing): {title}")
                    
                    song = genius.search_song(title)
                    if song:
                        embed_lirik = discord.Embed(title=song.title, description=song.lyrics[:2000], color=0x87CEEB)
                        embed_lirik.set_footer(text=f"Artist: {song.artist}")
                        await message.channel.send(embed=embed_lirik)
                    else:
                        await message.channel.send("Lirik tidak ketemu.")
    
    await bot.process_commands(message)

@bot.command()
async def lirik(ctx, *, judul_lagu):
    song = genius.search_song(judul_lagu)
    if song:
        await ctx.send(embed=discord.Embed(title=song.title, description=song.lyrics[:2000], color=0x87CEEB))
    else:
        await ctx.send("Lirik tidak ketemu.")

bot.run(TOKEN)
