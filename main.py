# Version: 1.9
# GitHub: https://github.com/Simoneeeeeeee/Discord-Select-Menu-Ticket-Bot
# Discord: discord.gg/ycZDpat7dB
import json
import threading

import discord
from discord import *
from discord.ext import commands, tasks

from cogs.media_commands import MediaCommand
from cogs.ticket_commands import Ticket_Command
from cogs.ticket_system import Ticket_System
from website.app import app

# This will get everything from the config.json file
with open("config.json", mode="r") as config_file:
    config = json.load(config_file)

BOT_TOKEN = config["token"]  # Your Bot Token from https://discord.dev
GUILD_ID = config["guild_id"]  # Your Server ID aka Guild ID
CATEGORY_ID1 = config["category_id_1"]
CATEGORY_ID2 = config["category_id_2"]
CATEGORY_ID3 = config["category_id_3"]
CATEGORY_ID4 = config["category_id_4"]
CATEGORY_ID5 = config["category_id_5"]

bot = commands.Bot(intents=discord.Intents.all(), command_prefix='!')


@bot.event
async def on_ready():
    print(f'Bot Started | {bot.user.name}')
    richpresence.start()
    threading.Thread(target=run_web_server).start()


# Bot Status, Counting all opened Tickets in the Server. You need to add/change things if you have more or less than 2 Categories
@tasks.loop(minutes=1)
async def richpresence():
    guild = bot.get_guild(GUILD_ID)
    category1 = discord.utils.get(guild.categories, id=int(CATEGORY_ID1))
    category2 = discord.utils.get(guild.categories, id=int(CATEGORY_ID2))
    category3 = discord.utils.get(guild.categories, id=int(CATEGORY_ID3))
    category4 = discord.utils.get(guild.categories, id=int(CATEGORY_ID4))
    category5 = discord.utils.get(guild.categories, id=int(CATEGORY_ID5))
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                        name=f'Tickets | {len(category1.channels) + len(category2.channels) + len(category3.channels) + len(category4.channels) + len(category5.channels)}'))


def run_web_server():
    print("Starting Web Server...")
    app.run(debug=True, use_reloader=False, port=25500, host="0.0.0.0")
    print("Web Server Started")


bot.add_cog(Ticket_System(bot))
bot.add_cog(Ticket_Command(bot))
bot.add_cog(MediaCommand(bot))
bot.run(BOT_TOKEN)
