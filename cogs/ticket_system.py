import asyncio
import io
import json
import sqlite3
from datetime import datetime

import chat_exporter
import discord
import pytz
from discord.ext import commands

# This will get everything from the config.json file
with open("config.json", mode="r") as config_file:
    config = json.load(config_file)

GUILD_ID = config["guild_id"]
TICKET_CHANNEL = config["ticket_channel_id"]
CATEGORY_ID1 = config["category_id_1"]
CATEGORY_ID2 = config["category_id_2"]
CATEGORY_ID3 = config["category_id_3"]
CATEGORY_ID4 = config["category_id_4"]
CATEGORY_ID5 = config["category_id_5"]
TEAM_ROLE1 = config["team_role_id_1"]
LOG_CHANNEL = config["log_channel_id"]
TIMEZONE = config["timezone"]
EMBED_TITLE = config["embed_title"]
EMBED_DESCRIPTION = config["embed_description"]

# This will create and connect to the database
conn = sqlite3.connect('Database.db')
cur = conn.cursor()

# Create the table if it doesn't exist
cur.execute("""CREATE TABLE IF NOT EXISTS ticket 
           (id INTEGER PRIMARY KEY AUTOINCREMENT, discord_name TEXT, discord_id INTEGER, ticket_channel TEXT, ticket_created TIMESTAMP)""")
conn.commit()


class Ticket_System(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Bot Loaded  | ticket_system.py ✅')
        self.bot.add_view(MyView(bot=self.bot))
        self.bot.add_view(CloseButton(bot=self.bot))
        self.bot.add_view(TicketOptions(bot=self.bot))

    # Closes the Connection to the Database when shutting down the Bot
    @commands.Cog.listener()
    async def on_bot_shutdown():
        cur.close()
        conn.close()


class MyView(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="support",
        placeholder="Choose a Ticket option",
        options=[
            discord.SelectOption(
                label="General Support",  # Name of the 1 Select Menu Option
                description="You will get help here!",  # Description of the 1 Select Menu Option
                emoji="❓",
                # Emoji of the 1 Option  if you want a Custom Emoji read this  https://github.com/Simoneeeeeeee/Discord-Select-Menu-Ticket-Bot/tree/main#how-to-use-custom-emojis-from-your-discors-server-in-the-select-menu
                value="support"  # Don't change this value otherwise the code will not work anymore!!!!
            ),
            discord.SelectOption(
                label="Player Report",  # Name of the 2 Select Menu Option
                description="You can report a player here!",  # Description of the 2 Select Menu Option
                emoji="⚠️",
                # Emoji of the 2 Option  if you want a Custom Emoji read this  https://github.com/Simoneeeeeeee/Discord-Select-Menu-Ticket-Bot/tree/main#how-to-use-custom-emojis-from-your-discors-server-in-the-select-menu
                value="report_player"  # Don't change this value otherwise the code will not work anymore!!!!
            ),
            discord.SelectOption(
                label="Staff Report",  # Name of the 2 Select Menu Option
                description="You can report a staff here!",  # Description of the 2 Select Menu Option
                emoji="📛",
                # Emoji of the 2 Option  if you want a Custom Emoji read this  https://github.com/Simoneeeeeeee/Discord-Select-Menu-Ticket-Bot/tree/main#how-to-use-custom-emojis-from-your-discors-server-in-the-select-menu
                value="report_staff"  # Don't change this value otherwise the code will not work anymore!!!!
            ),
            discord.SelectOption(
                label="Punishment Appeal",  # Name of the 2 Select Menu Option
                description="You can appeal a punishment here!",  # Description of the 2 Select Menu Option
                emoji="⚔️",
                # Emoji of the 2 Option  if you want a Custom Emoji read this  https://github.com/Simoneeeeeeee/Discord-Select-Menu-Ticket-Bot/tree/main#how-to-use-custom-emojis-from-your-discors-server-in-the-select-menu
                value="punishment_appeal"  # Don't change this value otherwise the code will not work anymore!!!!
            ),
            discord.SelectOption(
                label="Re-roll Request",  # Name of the 2 Select Menu Option
                description="You can request a re-roll here!",  # Description of the 2 Select Menu Option
                emoji="🎢",
                # Emoji of the 2 Option  if you want a Custom Emoji read this  https://github.com/Simoneeeeeeee/Discord-Select-Menu-Ticket-Bot/tree/main#how-to-use-custom-emojis-from-your-discors-server-in-the-select-menu
                value="reroll_request"  # Don't change this value otherwise the code will not work anymore!!!!
            )
        ]
    )
    async def callback(self, select, interaction):
        await interaction.response.defer()
        timezone = pytz.timezone(TIMEZONE)
        creation_date = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        user_name = interaction.user.name
        user_id = interaction.user.id

        cur.execute("SELECT discord_id FROM ticket WHERE discord_id=?",
                    (user_id,))  # Check if the User already has a Ticket open
        existing_ticket = cur.fetchone()

        if existing_ticket is None:
            if interaction.channel.id == TICKET_CHANNEL:
                guild = self.bot.get_guild(GUILD_ID)

                cur.execute("INSERT INTO ticket (discord_name, discord_id, ticket_created) VALUES (?, ?, ?)", (
                user_name, user_id,
                creation_date))  # If the User doesn't have a Ticket open it will insert the User into the Database and create a Ticket
                conn.commit()
                await asyncio.sleep(1)
                cur.execute("SELECT id FROM ticket WHERE discord_id=?",
                            (user_id,))  # Get the Ticket Number from the Database
                ticket_number = cur.fetchone()[0]

                if "support" in interaction.data['values']:
                    category = self.bot.get_channel(CATEGORY_ID1)
                if "report_player" in interaction.data['values']:
                    category = self.bot.get_channel(CATEGORY_ID2)
                if "report_staff" in interaction.data['values']:
                    category = self.bot.get_channel(CATEGORY_ID3)
                if "punishment_appeal" in interaction.data['values']:
                    category = self.bot.get_channel(CATEGORY_ID4)
                if "reroll_request" in interaction.data['values']:
                    category = self.bot.get_channel(CATEGORY_ID5)

                ticket_channel = await guild.create_text_channel(f"{ticket_number}-{interaction.user.name}",
                                                                 category=category,
                                                                 topic=f"{interaction.user.id}")

                await ticket_channel.set_permissions(guild.get_role(TEAM_ROLE1), send_messages=True, read_messages=True,
                                                     add_reactions=False,
                                                     # Set the Permissions for the Staff Team
                                                     embed_links=True, attach_files=True, read_message_history=True,
                                                     external_emojis=True)
                await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True,
                                                     add_reactions=False,
                                                     # Set the Permissions for the User
                                                     embed_links=True, attach_files=True, read_message_history=True,
                                                     external_emojis=True)
                await ticket_channel.set_permissions(guild.default_role, send_messages=False, read_messages=False,
                                                     view_channel=False)  # Set the Permissions for the @everyone role
                embed = discord.Embed(description=f'Welcome {interaction.user.mention},\n'
                                                  'describe your issue and our support will help you soon.',
                                      # Ticket Welcome message
                                      color=discord.colour.Color.blue())
                await ticket_channel.send(embed=embed, view=CloseButton(bot=self.bot))

                channel_id = ticket_channel.id
                cur.execute("UPDATE ticket SET ticket_channel = ? WHERE id = ?", (channel_id, ticket_number))
                conn.commit()

                embed = discord.Embed(description=f'📬 Ticket was Created! Look here --> {ticket_channel.mention}',
                                      color=discord.colour.Color.green())
                await interaction.followup.send(embed=embed, ephemeral=True)
                await asyncio.sleep(1)
                embed = discord.Embed(title=EMBED_TITLE, description=EMBED_DESCRIPTION,
                                      color=discord.colour.Color.blue())
                await interaction.message.edit(embed=embed, view=MyView(
                    bot=self.bot))  # This will reset the SelectMenu in the Ticket Channel

        else:
            embed = discord.Embed(title=f"You already have a open Ticket", color=0xff0000)
            await interaction.followup.send(embed=embed,
                                            ephemeral=True)  # This will tell the User that he already has a Ticket open
            await asyncio.sleep(1)
            embed = discord.Embed(title=EMBED_TITLE, description=EMBED_DESCRIPTION, color=discord.colour.Color.blue())
            await interaction.message.edit(embed=embed, view=MyView(
                bot=self.bot))  # This will reset the SelectMenu in the Ticket Channel


# First Button for the Ticket
class CloseButton(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.button(label="Delete Ticket 🎫", style=discord.ButtonStyle.blurple, custom_id="close")
    async def close(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = discord.Embed(title="Delete Ticket 🎫", description="Are you sure you want to delete this Ticket?",
                              color=discord.colour.Color.green())
        await interaction.response.send_message(embed=embed, view=TicketOptions(
            bot=self.bot))  # This will show the User the TicketOptions View
        await interaction.message.edit(view=self)


# Buttons to reopen or delete the Ticket
def convert_to_unix_timestamp(date_string):
    date_format = "%Y-%m-%d %H:%M:%S"
    dt_obj = datetime.strptime(date_string, date_format)
    berlin_tz = pytz.timezone('Europe/Berlin')
    dt_obj = berlin_tz.localize(dt_obj)
    dt_obj_utc = dt_obj.astimezone(pytz.utc)
    return int(dt_obj_utc.timestamp())


class TicketOptions(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.button(label="Delete Ticket 🎫", style=discord.ButtonStyle.red, custom_id="delete")
    async def delete_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        guild = self.bot.get_guild(GUILD_ID)
        channel = self.bot.get_channel(LOG_CHANNEL)
        ticket_id = interaction.channel.id

        cur.execute("SELECT id, discord_id, ticket_created FROM ticket WHERE ticket_channel=?", (ticket_id,))
        ticket_data = cur.fetchone()
        id, ticket_creator_id, ticket_created = ticket_data
        ticket_creator = guild.get_member(ticket_creator_id)

        ticket_creator_mention = ""

        if ticket_creator is None:
            ticket_creator = ticket_creator_id
            ticket_creator_mention = "<@" + ticket_creator + ">"
            print("ticket_creator was None, using: ", ticket_creator)
        else:
            ticket_creator_mention = ticket_creator.mention

        ticket_created_unix = convert_to_unix_timestamp(ticket_created)
        ticket_closed_unix = convert_to_unix_timestamp(
            datetime.now(pytz.timezone(TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S'))

        # Creating the Transcript
        military_time: bool = True
        transcript = await chat_exporter.export(interaction.channel, limit=200, tz_info=TIMEZONE,
                                                military_time=military_time, bot=self.bot)
        transcript_file = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{interaction.channel.name}.html"
        )

        with open(f"./transcripts/transcript-{interaction.channel.name}.html", "x") as f:
            f.write(transcript)

        embed = discord.Embed(description=f'Ticket is deleting in ~5 seconds.', color=0xff0000)
        transcript_info = discord.Embed(title=f"Ticket Deleted | {interaction.channel.name}",
                                        color=discord.colour.Color.blue())
        transcript_info.add_field(name="ID", value=id, inline=True)
        transcript_info.add_field(name="Opened by", value=ticket_creator_mention, inline=True)
        transcript_info.add_field(name="Closed by", value=interaction.user.mention, inline=True)
        transcript_info.add_field(name="Ticket Created", value=f"<t:{ticket_created_unix}:f>", inline=True)
        transcript_info.add_field(name="Ticket Closed", value=f"<t:{ticket_closed_unix}:f>", inline=True)

        await interaction.response.send_message(embed=embed)

        await channel.send(embed=transcript_info, file=transcript_file)
        await asyncio.sleep(3)
        await interaction.channel.delete(reason="Ticket Deleted")
        cur.execute("DELETE FROM ticket WHERE discord_id=?", (ticket_creator_id,))
        conn.commit()
