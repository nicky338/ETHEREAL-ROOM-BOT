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
async def on_ready():
    print(f'Bot Ethereal sudah ON!')

@bot.event
async def on_message(message):
    global last_played_song
    
    if message.author.name == "Jockie Music" and message.channel.id == TARGET_CHANNEL_ID:
        if message.embeds:
            embed = message.embeds[0]
            
            # CEK PROVIDER: Ini cara paling akurat buat nangkep YouTube
            # Jockie biasanya naruh provider di embed.provider.name
            provider_name = (embed.provider.name.lower() if embed.provider and embed.provider.name else "")
            
            # Deteksi kalau YouTube
            is_youtube = "youtube" in provider_name
            
            # Ambil teks buat jaga-jaga kalau provider-nya gak kedeteksi
            full_text = (embed.description or "") + " " + (embed.title or "") + " " + (embed.url or "")
            is_youtube_text = "youtube.com" in full_text.lower() or "youtu.be" in full_text.lower()
            
            if "Started playing" in full_text:
                # FILTER: Kalau terdeteksi YouTube, langsung kabur!
                if is_youtube or is_youtube_text:
                    print("YouTube terdeteksi via provider/link, skip lirik.")
                    return 

                # PEMERSIH JUDUL
                raw = full_text.split("Started playing")[-1].strip()
                clean_title = re.sub(r'[\(\[].*?[\)\]]', '', raw)
                title = clean_title.split(" by ")[0].strip()
                
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

bot.run(TOKEN)
