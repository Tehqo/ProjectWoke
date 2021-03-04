import discord
import os
import asyncio

from pafy import new
from dotenv import load_dotenv
from discord.ext import commands
from discord import FFmpegPCMAudio

load_dotenv()
SECRET_KEY = os.getenv("TOKEN")

client = commands.Bot(command_prefix = "+")


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
    await ctx.voice_client.disconnect()

@client.command(pass_context = True)
async def play(ctx, url):
    ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    channel = ctx.author.voice.channel
    if not client.voice_clients:
        voice = await channel.connect()
    else:
        voice = client.voice_clients[0]
    await ctx.send("**Playing** Music")
    video = new(url)
    audio = video.getbestaudio().url
    
    voice.play(FFmpegPCMAudio(audio, **ffmpeg_opts))
    voice.source = discord.PCMVolumeTransformer(voice.source, volume=0.25)
    voice.is_playing()


client.run(SECRET_KEY)