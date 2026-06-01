import discord
from discord.ext import commands
import lyricsgenius
import os
import re

# --- CONFIG ---
TOKEN = os.environ.get('DISCORD_TOKEN')
GENIUS_TOKEN = os.environ.get('GENIUS_ACCESS_TOKEN')
TARGET_CHANNEL_ID = 1510507327785144470 

# Setup Intents (PENTING: Pastikan Presence Intent aktif di Dev Portal)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

last_played_song = ""

@bot.event
async def on_ready():
    print(f'Ethereal Bot sudah ON dan siap beraksi secara Instan!')

@bot.event
async def on_message(message):
    global last_played_song
    
    # Filter: Bot cuma dengerin pesan dari Jockie dan di channel target
    if message.author.name == "Jockie Music" and message.channel.id == TARGET_CHANNEL_ID:
        if message.embeds:
            embed = message.embeds[0]
            text = (embed.description or "") + " " + " ".join([f.value for f in embed.fields])
            
            if "Started playing" in text:
                # Extract & Clean: Hapus kurung (), hapus [ ], ambil judul lagu
                raw = text.split("Started playing")[-1].strip()
                title_clean = re.sub(r'\(.*?\)', '', raw).split(" by ")[0].strip()
                title = title_clean.replace('[', '').replace(']', '')
                
                # Cek duplikasi
                if title != last_played_song:
                    last_played_song = title
                    
                    # Notif Estetik
                    await message.channel.send(f"**Auto-Sync (Playing):** *{title}*")
                    
                    # Update Status "Listening to" (Opsional, tapi bikin pro)
                    activity = discord.Activity(type=discord.ActivityType.listening, name=title)
                    await bot.change_presence(activity=activity)
                    
                    # Cari lirik
                    song = genius.search_song(title)
                    if song:
                        embed_lirik = discord.Embed(
                            title=song.title, 
                            description=song.lyrics[:2000], 
                            color=0x87CEEB
                        )
                        embed_lirik.set_footer(text=f"Artist: {song.artist}")
                        await message.channel.send(embed=embed_lirik)
    
    # WAJIB: Biar command !lirik tetep bisa dipake
    await bot.process_commands(message)

@bot.command()
async def lirik(ctx, *, judul_lagu):
    song = genius.search_song(judul_lagu)
    if song:
        await ctx.send(embed=discord.Embed(title=song.title, description=song.lyrics[:2000], color=0x87CEEB))
    else:
        await ctx.send("Lirik tidak ditemukan.")

bot.run(TOKEN)
