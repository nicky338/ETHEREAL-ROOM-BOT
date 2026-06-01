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
    print(f'ETHEREAL ROOM Bot Lirik udah ON, {bot.user} siap beraksi!')

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
        await ctx.send("Waduh, liriknya nggak ketemu nih. Coba cek judulnya lagi ya")

@bot.command()
async def sync(ctx):
    found = False
    # Kita cari 15 pesan terakhir di channel
    async for message in ctx.channel.history(limit=15):
        # Cek apakah author-nya adalah Jockie Music (pake 'ci', bukan 'oo')
        if "Jockie" in message.author.name: 
            # Kita cek teks pesannya
            if message.content and "Started playing" in message.content:
                # Bersihin teksnya buat dapetin judul lagu
                song_info = message.content.replace("Started playing", "").strip()
                
                await ctx.send(f"Ketemu! Jockie lagi muter: {song_info}. Bentar ya...")
                # Panggil fungsi lirik
                await lirik(ctx, judul_lagu=song_info)
                found = True
                break 
    
    if not found:
        await ctx.send("Waduh, nggak nemu pesan lagu dari Jockie Music di 15 chat terakhir, Ky.")

bot.run(TOKEN)
