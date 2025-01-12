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

with open("media.json", mode="r") as f:
    file = json.load(f)


class MediaCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.media_content = None
        try:
            self.media_content = file['media_message']
        except Exception:
            print("Failed to load media content from media.json")

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
        with open("media.json", mode="x") as f:
            json.dump({"media_message": text}, f, indent=4)
        await ctx.send(f'Media has been set to: {text}')
