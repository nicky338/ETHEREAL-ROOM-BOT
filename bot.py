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
    await bot.change_presence(activity=None)

@bot.event
async def on_message(message):
    global last_played_song
    
    # Cuma proses pesan dari Jockie Music di channel target
    if message.author.name == "Jockie Music" and message.channel.id == TARGET_CHANNEL_ID:
        if message.embeds:
            embed = message.embeds[0]
            
            # Gabungkan semua bagian embed untuk diperiksa
            content = f"{embed.title or ''} {embed.description or ''}"
            for field in embed.fields:
                content += f" {field.name} {field.value}"
            
            # DEBUG: Print ini ke log Railway biar kita tau apa yang dibaca bot
            print(f"DEBUG: Jockie sedang mengirim embed: {content[:100]}")

            # Deteksi lagu dengan mencari kata kunci "Started playing"
            if "Started playing" in content:
                # Ambil bagian setelah "Started playing"
                raw = content.split("Started playing")[-1].strip()
                # Ambil judul (asumsi format "Judul by Artis")
                title = raw.split(" by ")[0].strip()
                # Bersihkan dari markdown atau karakter aneh
                title = title.replace("*", "").replace("[", "").replace("]", "").strip()

                if title and title != last_played_song:
                    last_played_song = title
                    
                    # Konfirmasi kalau bot nangkep lagunya
                    await message.channel.send(f"Auto-Sync (Playing): **{title}**")
                    
                    # Cari lirik
                    song = genius.search_song(title)
                    if song:
                        embed_lirik = discord.Embed(title=song.title, description=song.lyrics[:2000], color=0x87CEEB)
                        embed_lirik.set_footer(text=f"Artist: {song.artist}")
                        await message.channel.send(embed=embed_lirik)
                    else:
                        await message.channel.send(f"Lyrics not found for: {title}")
    
    await bot.process_commands(message)

bot.run(TOKEN)
