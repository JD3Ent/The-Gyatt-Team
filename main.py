import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from gyatt_logic import calculate_susness, escalate_and_respond, add_sus_phrase, remove_sus_phrase, list_sus_phrases

# Load environment variables (for local dev)
load_dotenv()

# Discord bot setup with slash command support
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
slash = SlashCommand(bot, sync_commands=True)  # Enables slash commands


@bot.event
async def on_ready():
    """
    Event triggered when the bot is ready and connected to Discord.
    """
    print(f"We have logged in as {bot.user}")


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
@slash.slash(name="add_sus_phrase", description="Add a new phrase to the sus library.")
async def add_sus_phrase_command(ctx: SlashContext, phrase: str, score: float):
    """
    Adds a new phrase to the SUS_PHRASES library via a slash command.

    Args:
        ctx (SlashContext): The context of the slash command.
        phrase (str): The new phrase to add.
        score (float): The susness score to assign to the phrase.
    """
    response = add_sus_phrase(phrase, score)  # Delegated to gyatt_logic.py
    await ctx.send(response)


# Slash Command: Remove a Sus Phrase
@slash.slash(name="remove_sus_phrase", description="Remove a phrase from the sus library.")
async def remove_sus_phrase_command(ctx: SlashContext, phrase: str):
    """
    Removes a phrase from the SUS_PHRASES library via a slash command.

    Args:
        ctx (SlashContext): The context of the slash command.
        phrase (str): The phrase to remove.
    """
    response = remove_sus_phrase(phrase)  # Delegated to gyatt_logic.py
    await ctx.send(response)


# Slash Command: List All Sus Phrases
@slash.slash(name="list_sus_phrases", description="List all phrases in the sus library.")
async def list_sus_phrases_command(ctx: SlashContext):
    """
    Lists all phrases in the SUS_PHRASES library via a slash command.

    Args:
        ctx (SlashContext): The context of the slash command.
    """
    response = list_sus_phrases()  # Delegated to gyatt_logic.py
    await ctx.send(response)


# Run the bot using the token from environment variables (GitHub Secrets or .env file)
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if DISCORD_BOT_TOKEN is None:
    raise ValueError("DISCORD_BOT_TOKEN not found in environment variables.")
bot.run(DISCORD_BOT_TOKEN)
