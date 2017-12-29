"""
dependencies: ffmpeg, opus (install at system lvl)

"""
import discord
from discord.ext import commands
from discord_token import *
import subprocess
import sys
import asyncio
import youtube_dl
# import opuslib

# set up discord
client = commands.Bot(command_prefix='!')


def get_channel(client, channel_name):
    for channel in client.get_all_channels():
        if channel.name == channel_name:
            return channel
    return None


async def print_discord(string, channel='general'):
    dest_channel = get_channel(client, channel)
    await client.send_message(dest_channel, string)
    return 0


@client.event
async def on_ready():
    print('logged in')


@client.command()
async def play():
    # discord.opus.load_opus(name='opus')
    channel_name = 'Music'
    voice_client = await client.join_voice_channel(channel=get_channel(client=client, channel_name=channel_name))
    if voice_client.is_connected() is True and discord.opus.is_loaded() is True:
        await print_discord("Bot joined voice channel " + channel_name + " successfully.", channel='general')

        url = 'https://www.youtube.com/watch?v=TbdZiu3Rarw'
        player = await voice_client.create_ytdl_player(url=url, use_avconv=True)
        player.start()

client.run(TOKEN)
