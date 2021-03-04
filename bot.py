import discord
import os
import asyncio
from youtube_dl import YoutubeDL

from pafy import new
from dotenv import load_dotenv
from discord.ext import commands
from discord import FFmpegPCMAudio

load_dotenv()
SECRET_KEY = os.getenv("TOKEN")

client = commands.Bot(command_prefix = "+")

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

songs = []
songInfo = []


# Helper Functions
async def play_next(ctx, source):
    if len(songs) > 1:
        del songs[0]
        del songInfo[0]
        URL = songs[0]
        TITLE = songInfo[0]
        vc = client.voice_clients[0]
        vc.stop()
        vc.play(FFmpegPCMAudio(source=URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx, source))
        await ctx.send(f"**Woke is now playing: ** {songInfo[0]}")
# End of Helper Functions

@client.event
async def on_ready():
    print("Bot is ready!")

@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(client.latency * 1000)} ms")

@client.command()
async def join(ctx):
    channel = ctx.message.author.voice.channel
    await channel.connect()

@client.command()
async def leave(ctx):
    songInfo = []
    songs = []
    await ctx.voice_client.disconnect()

@client.command(pass_context = True)
async def play(ctx, url):
    channel = ctx.author.voice.channel
    if not client.voice_clients:
        voice = await channel.connect()
    else:
        voice = client.voice_clients[0]

    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
    
    TITLE = info['title']
    songInfo.append(TITLE)

    URL = info['formats'][0]['url']
    songs.append(URL)

    await ctx.send(f"Added {TITLE}")

    if not voice.is_playing():
        voice.play(FFmpegPCMAudio(source=URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx, URL))
        await ctx.send(f"**Woke is now playing: ** {info['title']}")
        voice.is_playing()

@client.command(pass_context=True)
async def skip(ctx):
    await play_next(ctx, songs[0])

@client.command(pass_context = True)
async def queue(ctx):
    msg = "**Woke's Queue:** \n"
    for i in range(len(songInfo)):
        msg = msg + str(i+1) + ". " + songInfo[i] + "\n"
    
    await ctx.send(msg)
        

client.run(SECRET_KEY)

