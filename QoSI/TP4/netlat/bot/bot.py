from datetime import datetime
from os import path, listdir
import socket
import json
import time
import traceback
import yaml
import discord
from discord.ext import commands , tasks
import json
import pandas as pd
import os
from io import StringIO
import argparse as ap
import random


import utilities as utilities
from network import public_ip


intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix = '*',
    case_insensitive=True,
    intents=intents)

message_dns = None


cogs_blacklist = []


## EXTENSIONS

class Latency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def __module__():
        return 'latency'

    @commands.command()
    async def get_dns(self, ctx):
        """Joins a voice channel"""
        channel = bot.get_channel(bot.config['channels']["voice"])

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()
        time.sleep(1)
        await ctx.voice_client.disconnect()

    @commands.command(name='manual_latency')
    async def manual_test_latency(self, ctx):
        event1.start()
        sleep(1)
        event1.stop()

    @commands.command(name='stop_latency')
    async def stop_latency(self, ctx):
        event1.stop()

    @commands.command(name='start_latency')
    async def start_latency(self, ctx):
        event1.start()

    @commands.command(name='lat_freq', aliases=['latency_frequency'],description='Edits the frequency as the bot sends its latency in seconds')
    async def set_frequency(self, ctx, time):
        event1.change_interval(seconds=int(time))
        await ctx.send(f"Frequency set to {time} seconds")


class Scraper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def __module__():
        return 'scraper'


    @commands.command()
    async def save(self, ctx = None, channel = None):
        try:
            if ctx is None:
                if channel is None:
                    channel = bot.get_channel(bot.config['channels']["logs"])
                ctx = channel

            if not bot.main:
                return
            if bot.token != "server":
                return
            
            timestamp = utilities.Timestamp.get_formatted().replace(" ", "_").replace(":","h")
            per_channel = {}
            """Scrapes a channel"""
            async with ctx.typing():
                category = discord.utils.get(ctx.guild.categories, id=bot.config['channels']["category"])
                for channel in category.channels:
                    await ctx.send(f"Fetching channel {channel.name}")
                    per_channel[channel.name] = []
                    async for message in channel.history(limit=None, oldest_first=True):
                        json_message = message.content.strip().replace("```json","").replace("```","").replace("\\","").replace("\n","")
                        json_object = {"hostname":channel.name}
                        json_object.update(json.loads(json_message))
                        per_channel[channel.name].append(json_object)


                    os.makedirs(f"{bot.DATASETS_PATH}{channel.name}", exist_ok=True)

                    with open(f"{bot.DATASETS_PATH}{channel.name}/channel_{channel.name}_date_{timestamp}.json", "w") as file:
                        json_full_object = per_channel[channel.name]
                        json.dump(json_full_object, file, indent=4)
                    # Send the file just for testing
                    await ctx.send(file=discord.File(f"{bot.DATASETS_PATH}{channel.name}/channel_{channel.name}_date_{timestamp}.json"))
                    await channel.purge(limit=None)

            await ctx.send("Finished scraping")

        except Exception as e:
            print(e)
            print(traceback.format_exc())
            await ctx.send(f"Error: {e}")
            await ctx.send(f"Error: {traceback.format_exc()}")

    @commands.command()
    async def start_save(self, ctx):
        event2.start()

    @commands.command()
    async def stop_save(self, ctx):
        event2.stop()

    @commands.command()
    async def change_prefix(self, ctx, bot_client: discord.Member, prefix):
        if bot_client.id == self.bot.application_id:
            bot.command_prefix = prefix
            await ctx.send(f"Prefix changed to {prefix}")
        else:
            await ctx.send("Bot not found")


async def main(mode, token):
    #adding to bot object directories
    bot.DATASETS_PATH = 'datasets/'
    
    if not mode:
        global cogs_blacklist
        cogs_blacklist = ['scraper']

    bot.main = mode
    bot.token = token

    with open("config.yaml", "r") as file:
        bot.config = yaml.safe_load(file)
        file.close()

    #load extensions
    await extensions_loader(create_list_extensions())

    await bot.start(bot.config['credentials'][token])

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='*help'))

    async def get_dns():
        """Joins a voice channel"""
        channel = bot.get_channel(bot.config['channels']["voice"])

        await channel.connect()
        time.sleep(1)
        for vc in bot.voice_clients:
            await vc.disconnect()


    #default color for embeds
    bot.embed_color = get_bot_color(bot)

    embed = discord.Embed(
        title="Starting up",
        description=f"bot started at {str(datetime.now())}",
        color=bot.embed_color)

    embed.add_field(
        name="Extensions loaded",
        value=bot.extensions_list_loaded,
        inline=True)

    embed.add_field(
        name="Extensions failed",
        value=bot.extensions_list_failed,
        inline=True)

    blacklist = "No Cogs in Blaklist"
    if len(cogs_blacklist) > 0:
        blacklist = '\n'.join(cogs_blacklist)

    embed.add_field(
        name="Blacklist",
        value=blacklist,
        inline=False)


    bot.log_channel = bot.get_channel(bot.config['channels']["logs"])

    app_info = await bot.application_info()

    await app_info.owner.send(embed=embed)

    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print('-----------------------------')
    print('Servers:')
    for guild in bot.guilds:
        print(guild.name)
    print('-----------------------------')
    print(bot.embed_color)
    print(bot.command_prefix)


    if bot.main:
        await create(bot)
    await get_dns()

    if not bot.main:
        event1.start()


@tasks.loop(minutes=20)
async def event1():
    try:
        channel = bot.get_channel(bot.config['channels']["data"])
        json_object = {"latency": round(bot.latency * 1000,3), "public_ip": public_ip() , "hostname": socket.gethostname(), "timestamp": utilities.Timestamp.get_timestamp(), "lang":"pyhton"}
        await channel.send("```json\n" + str(json_object).replace("'", "\"") + "\n```")
    except Exception as e:
        print(e)
        print(traceback.format_exc())


@tasks.loop(hours=24)
async def event2():
    try:
        scrap = Scraper(bot)
        channel = bot.get_channel(bot.config['channels']["logs"])
        await scrap.save(channel)
    except Exception as e:
        bot.log_channel.send(f"Error: {e}")
        bot.log_channel.send(f"Error: {traceback.format_exc()}")
        print(e)
        print(traceback.format_exc())



@bot.event
async def on_message(message):


    ##if message.author.id == 773625025155956746:
    ##    ctx = await bot.get_context(message)
    ##    await bot.invoke(ctx)

    await bot.process_commands(message)


def get_bot_color(bot):
    big_guild, color = 0, 0xffff00
    for guild in bot.guilds:
        if len(guild.members) > big_guild:
            big_guild, color = len(guild.members), guild.me.color
    return color

def create_list_extensions():
#create a list with possible extensions
    extensions_list = [Latency, Scraper]

    extensions_list = list(filter(
            lambda x: "__" not in x.__module__() and x.__module__() not in cogs_blacklist,
            extensions_list))

    return extensions_list


async def extensions_loader(extensions):
#try to load extensions
    loaded = ""
    failed = ""
    for extension in extensions:
        try:
            await bot.add_cog(extension(bot))
            loaded = loaded + "\n" + extension.__module__()
        except Exception as e:
            exc = f'{type(e).__name__}: {e}'
            print(f'Failed to load extension: {extension}\n{exc}')
            failed = failed + "\n" + ('**{}**:{}'.format(extension, exc))
            print(traceback.format_exc())

    bot.extensions_list_loaded = loaded
    bot.extensions_list_failed = "No cogs failed to load"
    if failed != "":
        bot.extensions_list_failed = failed

async def create(bot):
    try:
        host = socket.gethostname()
        guild = bot.get_guild(bot.config['guild']['id'])
        category = discord.utils.get(guild.categories, id=bot.config['channels']["category"])
        
        if bot.config['channels'].get("data", None) is None or discord.utils.get(category.channels, name=host) is None:
            channel = await guild.create_text_channel(host, category=category)
            await bot.log_channel.send(f"Channel {host} created")
            bot.config['channels']["data"] = channel.id
            bot.config['channels']["data_str"] = f"{channel.id}"
            with open("config.yaml", "w") as file:
                yaml.safe_dump(bot.config, file)
            with open("config.yaml", "r") as file:
                bot.config = yaml.safe_load(file)
        else:
            await bot.log_channel.send(f"Channel {host} already exists")
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        await bot.log_channel.send(f"Error: {e}")
        await bot.log_channel.send(f"Error: {traceback.format_exc()}")

import asyncio

def _run_from_modules(boolean, token, prefix = "*"):
    global bot
    bot.command_prefix = prefix
    asyncio.run(main(boolean,token))

if __name__ == '__main__':
    ap = ap.ArgumentParser()
    ap.add_argument('--m',action='store_true', help='Main mode')
    ap.add_argument('--token','-t',action= 'store' , help='Which token to use', choices=['server','main', 'workers'], default='server')
    args = ap.parse_args()
    asyncio.run(main(args.m, args.token))

