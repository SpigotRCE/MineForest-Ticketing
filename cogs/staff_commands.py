import discord
import json
import chat_exporter
import io
import pytz
from datetime import datetime
import sqlite3
from discord import *
from discord.ext import commands
from discord.ext.commands import has_permissions
from cogs.ticket_system import MyView

#This will get everything from the config.json file
with open("config.json", mode="r") as config_file:
    config = json.load(config_file)


class Staff_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.media_content = None
        try:
            self.media_content = config['media_message']
        except Exception:
            print("Failed to load media content from config.json")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Bot Loaded  | staff_commands.py ✅')

    @commands.command(name="media")
    async def media(self, ctx):
        if self.media_content:
            await ctx.send(self.media_content)
        else:
            await ctx.send("No media set. Use !setmedia to set it.")

    @commands.command(name="setmedia")
    @has_permissions(administrator=True)
    async def set_media(self, ctx, *, text: str):
        self.media_content = text
        with open("config.json", mode="w") as f:
            json.dump({"media_message": text}, f, indent=4)
        await ctx.send(f'Media has been set to: {text}')
