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
    async for message in ctx.channel.history(limit=15):
        if "Jockie" in message.author.name and message.embeds:
            embed = message.embeds[0]
            
            # Kita cek setiap field di dalam embed
            # Biasanya Jockie naruh info lagu di field pertama atau deskripsi
            search_text = ""
            
            # Cek di deskripsi
            if embed.description:
                search_text += embed.description
            
            # Cek di fields (ini biasanya tempat "Started playing...")
            for field in embed.fields:
                search_text += " " + field.value
            
            # Sekarang kita cari "Started playing" di semua teks yang udah dikumpulin
            if "Started playing" in search_text:
                # Ambil teks setelah "Started playing"
                # Kita bersihin biar dapet judul lagu yang bersih
                song_info = search_text.split("Started playing")[-1].strip()
                
                await ctx.send(f"Ketemu! Jockie lagi muter: {song_info}. Bentar ya...")
                await lirik(ctx, judul_lagu=song_info)
                found = True
                break
    
    if not found:
        await ctx.send("Waduh, Jockie-nya masih sembunyi nih. Gak nemu data lagu di embed-nya.")

bot.run(TOKEN)
