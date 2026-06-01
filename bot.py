import discord
from discord.ext import commands
import lyricsgenius
import os

# --- CONFIG ---
TOKEN = os.environ.get('DISCORD_TOKEN')
GENIUS_TOKEN = os.environ.get('GENIUS_ACCESS_TOKEN')

# Setup Intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Setup Genius
genius = lyricsgenius.Genius(GENIUS_TOKEN)

@bot.event
async def on_ready():
    # Status bot
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="!lirik <judul lagu>"))
    print(f'ETHEREAL ROOM Bot Lirik udah ON, {bot.user} siap beraksi! 🗿')

@bot.command()
async def lirik(ctx, *, judul_lagu):
    await ctx.send(f"Bentar, lagi nyari lirik buat: {judul_lagu}...")
    song = genius.search_song(judul_lagu)
    if song:
        lirik_text = song.lyrics[:2000] 
        embed = discord.Embed(title=song.title, description=lirik_text, color=0x87CEEB)
        embed.set_footer(text=f"Artist: {song.artist}")
        await ctx.send(embed=embed)
    else:
        await ctx.send("Waduh, liriknya nggak ketemu nih, Ky. Coba cek judulnya lagi!")

@bot.command()
async def sync(ctx):
    # Bot ngebaca 5 pesan terakhir di channel buat nyari Jookie Music
    found = False
    async for message in ctx.channel.history(limit=5):
        # Cek apakah pengirimnya si Jookie Music
        if message.author.name == "Jookie Music": 
            # Ngambil judul lagu dari field/text Jookie Music
            # Biasanya Jookie naruh judul di field atau description embed
            if message.embeds:
                # Kita ambil teks dari field pertama kalau ada, atau dari description
                song_info = message.embeds[0].description
                
                # Pembersih teks sederhana biar bot nggak bingung
                if "Started playing" in song_info:
                    song_info = song_info.replace("Started playing", "").strip()
                
                await ctx.send(f"Ditemukan! Jookie lagi muter: {song_info}. Lagi nyari liriknya ya...")
                
                # Langsung panggil fungsi lirik
                await lirik(ctx, judul_lagu=song_info)
                found = True
                break 
    
    if not found:
        await ctx.send("Waduh, nggak nemu pesan lagu dari Jookie Music di 5 chat terakhir, Ky.")

bot.run(TOKEN)
