import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from gyatt_logic import calculate_susness, escalate_and_respond, add_sus_phrase, remove_sus_phrase, list_sus_phrases
from flask import Flask, render_template
import asyncio
import threading

# Load environment variables
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not DISCORD_BOT_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN not found in environment variables.")

# Discord Bot Setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Flask Web Server Setup
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

async def bot_main():
    """Main function to run the Discord bot."""
    async with bot:
        bot.tree.copy_global_to(guild=None)  # Ensure commands are global
        await bot.start(DISCORD_BOT_TOKEN)

def run_server():
    """Runs the Flask web server."""
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

@bot.event
async def on_ready():
    """Event triggered when the bot is ready."""
    print(f"We have logged in as {bot.user}")
    try:
        await tree.sync()  # Sync slash commands globally
        print("Slash commands synced successfully!")
    except Exception as e:
        print(f"Error syncing slash commands: {e}")

@bot.event
async def on_message(message):
    """Event triggered when a message is sent."""
    if message.author == bot.user or not message.content.strip():
        return

    sus_score = calculate_susness(message.content)

    if sus_score > 0:
        await escalate_and_respond(message.author, message, sus_score)

# Slash Command: Add a New Sus Phrase
@tree.command(name="add_sus_phrase", description="Add a new phrase to the sus library.")
async def add_sus_phrase_command(interaction: discord.Interaction, phrase: str, score: float):
    """Adds a new phrase to the SUS_PHRASES library."""
    response = add_sus_phrase(phrase, score)  # Delegated to gyatt_logic.py
    await interaction.response.send_message(response)

# Slash Command: Remove a Sus Phrase
@tree.command(name="remove_sus_phrase", description="Remove a phrase from the sus library.")
async def remove_sus_phrase_command(interaction: discord.Interaction, phrase: str):
    """Removes a phrase from the SUS_PHRASES library."""
    response = remove_sus_phrase(phrase)  # Delegated to gyatt_logic.py
    await interaction.response.send_message(response)

# Slash Command: List All Sus Phrases
@tree.command(name="list_sus_phrases", description="List all phrases in the sus library.")
async def list_sus_phrases_command(interaction: discord.Interaction):
    """Lists all phrases in the SUS_PHRASES library."""
    response = list_sus_phrases()  # Delegated to gyatt_logic.py
    await interaction.response.send_message(response)

if __name__ == "__main__":
    # Start the Flask web server in a separate thread
    threading.Thread(target=run_server, daemon=True).start()
    
    # Run the Discord bot in the main thread
    asyncio.run(bot_main())
    
