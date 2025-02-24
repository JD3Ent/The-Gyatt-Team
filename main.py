import os
import discord
from discord.ext import commands
from discord import app_commands  # For native slash commands
from dotenv import load_dotenv
from gyatt_logic import calculate_susness, escalate_and_respond, add_sus_phrase, remove_sus_phrase, list_sus_phrases
from flask import Flask
import threading

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
threading.Thread(target=run_server).start()

# Load environment variables (for local development or production)
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if DISCORD_BOT_TOKEN is None:
    raise ValueError("DISCORD_BOT_TOKEN not found in environment variables.")

# Discord Bot Setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Required for reading message content

bot = commands.Bot(command_prefix="!", intents=intents)

# Slash Command Tree (for native slash commands)
tree = bot.tree

@bot.event
async def on_ready():
    """
    Event triggered when the bot is ready and connected to Discord.
    """
    print(f"We have logged in as {bot.user}")
    # Sync slash commands with Discord
    try:
        await tree.sync()
        print("Slash commands synced successfully!")
    except Exception as e:
        print(f"Error syncing slash commands: {e}")

@bot.event
async def on_message(message):
    """
    Event triggered when a message is sent in a channel the bot has access to.
    """
    # Ignore messages from the bot itself or empty messages
    if message.author == bot.user or not message.content.strip():
        return

    # Calculate susness dynamically using spaCy (delegated to gyatt_logic.py)
    sus_score = calculate_susness(message.content)

    # If a sus score is detected, escalate and respond accordingly
    if sus_score > 0:
        await escalate_and_respond(message.author, message, sus_score)

# Slash Command: Add a New Sus Phrase
@tree.command(name="add_sus_phrase", description="Add a new phrase to the sus library.")
async def add_sus_phrase_command(interaction: discord.Interaction, phrase: str, score: float):
    """
    Adds a new phrase to the SUS_PHRASES library via a slash command.

    Args:
        interaction (discord.Interaction): The context of the slash command.
        phrase (str): The new phrase to add.
        score (float): The susness score to assign to the phrase.
    """
    response = add_sus_phrase(phrase, score)  # Delegated to gyatt_logic.py
    await interaction.response.send_message(response)

# Slash Command: Remove a Sus Phrase
@tree.command(name="remove_sus_phrase", description="Remove a phrase from the sus library.")
async def remove_sus_phrase_command(interaction: discord.Interaction, phrase: str):
    """
    Removes a phrase from the SUS_PHRASES library via a slash command.

    Args:
        interaction (discord.Interaction): The context of the slash command.
        phrase (str): The phrase to remove.
    """
    response = remove_sus_phrase(phrase)  # Delegated to gyatt_logic.py
    await interaction.response.send_message(response)

# Slash Command: List All Sus Phrases
@tree.command(name="list_sus_phrases", description="List all phrases in the sus library.")
async def list_sus_phrases_command(interaction: discord.Interaction):
    """
    Lists all phrases in the SUS_PHRASES library via a slash command.

    Args:
        interaction (discord.Interaction): The context of the slash command.
    """
    response = list_sus_phrases()  # Delegated to gyatt_logic.py
    await interaction.response.send_message(response)

# Run the bot using the token from environment variables (GitHub Secrets or .env file)
bot.run(DISCORD_BOT_TOKEN)
