import discord
from discord.ext import commands
import lyricsgenius
import os  # <--- INI TAMBAHIN DI SINI

# --- CONFIG ---
TOKEN = os.environ.get('DISCORD_TOKEN')
GENIUS_TOKEN = os.environ.get('GENIUS_TOKEN')
# ... (lanjutan kode lainnya sama)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

@bot.event
async def on_ready():
    print(f'ETHEREAL ROOM Bot Lirik udah ON, {bot.user} siap beraksi! 🗿')

@bot.command()
async def lirik(ctx, *, judul_lagu):
    await ctx.send(f"Bentar, lagi nyari lirik buat: {judul_lagu}...")
    song = genius.search_song(judul_lagu)
    if song:
        lirik_text = song.lyrics[:1000] 
        embed = discord.Embed(title=song.title, description=lirik_text, color=0x87CEEB)
        embed.set_footer(text=f"Artist: {song.artist}")
        await ctx.send(embed=embed)
    else:
        await ctx.send("Waduh, liriknya nggak ketemu nih, Ky. Coba cek judulnya lagi!")

bot.run(TOKEN)