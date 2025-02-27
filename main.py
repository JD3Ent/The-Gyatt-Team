import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from gyatt_logic import calculate_susness, escalate_and_respond, add_sus_phrase, remove_sus_phrase, list_sus_phrases
from flask import Flask
import threading
import asyncio

# Load environment variables
load_dotenv()

# Retrieve Discord bot token from environment variables
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not DISCORD_BOT_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN not found in environment variables.")

# Retrieve the Discord server ID from environment variables
GUILD_ID = os.getenv("GUILD_ID")
if not GUILD_ID:
    raise ValueError("GUILD_ID not found in environment variables. Make sure to set it in your Render environment or .env file")
else:
    try:
        GUILD_ID = int(GUILD_ID)  # Convert to integer if it's a string
    except ValueError:
        raise ValueError("GUILD_ID must be an integer. Please check your Render environment or .env file.")

# Retrieve the Discord application ID from environment variables
APPLICATION_ID = os.getenv("APPLICATION_ID")
if not APPLICATION_ID:
    raise ValueError("APPLICATION_ID not found in environment variables. Make sure to set it in your Render environment or .env file")
else:
    try:
        APPLICATION_ID = int(APPLICATION_ID)  # Convert to integer if it's a string
    except ValueError:
        raise ValueError("APPLICATION_ID must be an integer. Please check your Render environment or .env file.")

# Discord Bot Setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, application_id=APPLICATION_ID)
tree = bot.tree

# Flask Web Server Setup
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_server():
    # Get the PORT from environment variables (default to 8080 if not set)
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# Start the web server in a separate thread
threading.Thread(target=run_server, daemon=True).start()

# Remove bot_main function
# Remove the asyncio.run(bot_main()) from if __name__ == "__main__":

async def handle_commands(interaction, response_func, *args):
    """Handles command execution with rate limit handling."""
    try:
        await response_func(interaction, *args)
    except discord.errors.HTTPException as e:
        if e.status == 429:
            print(f"Rate limit exceeded: {e}")
            retry_after = e.retry_after if hasattr(e, 'retry_after') else 5  # Default to 5 seconds
            print(f"Waiting {retry_after} seconds before retrying...")
            await asyncio.sleep(retry_after)
            await handle_commands(interaction, response_func, *args)  # Retry
        else:
            print(f"An unexpected error occurred: {e}")
            if interaction and hasattr(interaction, 'response') and not interaction.response.is_done():
                await interaction.response.send_message("An error occurred while processing your command.", ephemeral=True)

@bot.event
async def on_ready():
    """Event triggered when the bot is ready."""
    print(f"We have logged in as {bot.user}")

    # Sync slash commands to the specified guild
    try:
        guild = discord.Object(id=GUILD_ID) # Now using GUILD_ID from environment variables
        # tree.copy_global_to(guild=guild) # This line is often problematic
        synced = await tree.sync(guild=guild)

        print(f"Successfully synced {len(synced)} commands to guild {GUILD_ID}")
    except discord.errors.HTTPException as e:
        if e.status == 429:
            print(f"Rate limit exceeded while syncing commands: {e}")
            retry_after = e.retry_after if hasattr(e, 'retry_after') else 5
            print(f"Waiting {retry_after} seconds before retrying...")
            await asyncio.sleep(retry_after)
            await on_ready()  # Retry the sync
        
@bot.event
async def on_message(message):
    """Event triggered when a message is sent."""
    if message.author == bot.user or not message.content.strip():
        return

    # Calculate susness dynamically (delegated to gyatt_logic.py)
    sus_score = calculate_susness(message.content)

    # If a sus score is detected, escalate and respond accordingly
    if sus_score > 0:
        try:
            await escalate_and_respond(message.author, message, sus_score)
        except discord.errors.HTTPException as e:
            if e.status == 429:
                print(f"Rate limit exceeded in on_message: {e}")
                retry_after = e.retry_after if hasattr(e, 'retry_after') else 5
                print(f"Waiting {retry_after} seconds before retrying...")
                await asyncio.sleep(retry_after)
                await on_message(message)  # Retry processing the message
            else:
                print(f"An unexpected error occurred in on_message: {e}")

# Slash Command: Add a New Sus Phrase
@tree.command(name="add_sus_phrase", description="Add a new phrase to the sus library.")
async def add_sus_phrase_command(interaction: discord.Interaction, phrase: str, score: float):
    """Adds a new phrase to the SUS_PHRASES library."""
    await handle_commands(interaction, _add_sus_phrase_command, phrase, score)

async def _add_sus_phrase_command(interaction: discord.Interaction, phrase: str, score: float):
    response = add_sus_phrase(phrase, score)  # Delegated to gyatt_logic.py
    await interaction.response.send_message(response)

# Slash Command: Remove a Sus Phrase
@tree.command(name="remove_sus_phrase", description="Remove a phrase from the sus library.")
async def remove_sus_phrase_command(interaction: discord.Interaction, phrase: str):
    """Removes a phrase from the SUS_PHRASES library."""
    await handle_commands(interaction, _remove_sus_phrase_command, phrase)

async def _remove_sus_phrase_command(interaction: discord.Interaction, phrase: str):
    response = remove_sus_phrase(phrase)  # Delegated to gyatt_logic.py
    await interaction.response.send_message(response)

# Slash Command: List All Sus Phrases
@tree.command(name="list_sus_phrases", description="List all phrases in the sus library.")
async def list_sus_phrases_command(interaction: discord.Interaction):
    """Lists all phrases in the SUS_PHRASES library."""
    await handle_commands(interaction, _list_sus_phrases_command)

async def _list_sus_phrases_command(interaction: discord.Interaction):
    response = list_sus_phrases()  # Delegated to gyatt_logic.py
    await interaction.response.send_message(response)

if __name__ == "__main__":
    # Start the Flask web server in a separate thread
    threading.Thread(target=run_server, daemon=True).start()

    # Run the Discord bot in the main thread
    bot.run(DISCORD_BOT_TOKEN) # call bot.run directly
