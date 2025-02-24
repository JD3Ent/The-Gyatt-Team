import discord
import os
import random
import asyncio
from dotenv import load_dotenv  # For loading environment variables
from calculations import calculate_final_sus_points  # Dynamic multiplier system
from library.sus_phrases import calculate_susness
from library.gay_police_responses import GAY_POLICE_FINAL_RESPONSES, GAY_POLICE_ESCALATION_RESPONSES
from library.gay_army_responses import GAY_ARMY_FINAL_RESPONSES, GAY_ARMY_ESCALATION_RESPONSES
from library.gayvie_responses import GAYVIE_FINAL_RESPONSES, GAYVIE_ESCALATION_RESPONSES
from library.gay_airforce_responses import GAY_AIRFORCE_FINAL_RESPONSES, GAY_AIRFORCE_ESCALATION_RESPONSES
from bots.gay_police import gay_police_interaction
from bots.gay_army import gay_army_interaction
from bots.gayvie import gayvie_interaction
from bots.gay_airforce import gay_airforce_interaction

# Slash commands support
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

# Load environment variables (for local dev)
load_dotenv()

# Discord bot setup with slash command support
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
slash = SlashCommand(bot, sync_commands=True)  # Enables slash commands

# Persistent tally tracking files
POLICE_RECORD_FILE = "police_record.txt"
NUKED_RECORD_FILE = "nuked.py"

# Active user interaction tracking
active_interactions = {}  # {user_id: {"sus_score": int, "timeout": asyncio.Task}}

# Thresholds for escalation
GAY_POLICE_THRESHOLD = 5
GAY_ARMY_NAVY_THRESHOLD = 10
GAY_AIRFORCE_THRESHOLD = 15

# Timeout for ending an interaction (in seconds)
INTERACTION_TIMEOUT = 60


# Helper function: Load police records from file
def load_police_records():
    try:
        with open(POLICE_RECORD_FILE, "r") as f:
            records = {}
            for line in f.readlines():
                user_id, tally = line.strip().split(":")
                records[user_id] = float(tally)  # Store as float for precision
            return records
    except FileNotFoundError:
        return {}


# Helper function: Save police records to file
def save_police_records(records):
    with open(POLICE_RECORD_FILE, "w") as f:
        for user_id, tally in records.items():
            f.write(f"{user_id}:{tally:.2f}\n")


# Helper function: Log users nuked by the final attack into a file (updates if already exists)
def log_nuked_user(user_id, username, total_points):
    nuked_users = load_nuked_users()
    updated = False

    # Update existing record if user already exists in nuked list
    for user in nuked_users:
        if user["id"] == str(user_id):
            user["points"] = total_points  # Update their total points
            updated = True

    # If user is new, add them to the list
    if not updated:
        nuked_users.append({"id": str(user_id), "username": username, "points": total_points})

    # Write back to file
    try:
        with open(NUKED_RECORD_FILE, "w") as f:
            for user in nuked_users:
                f.write(f"{user['id']}:{user['username']}:{user['points']:.2f}\n")
    except Exception as e:
        print(f"Failed to log nuked user: {e}")


# Helper function: Load nuked users from file
def load_nuked_users():
    try:
        with open(NUKED_RECORD_FILE, "r") as f:
            nuked_users = []
            for line in f.readlines():
                user_id, username, points = line.strip().split(":")
                nuked_users.append({"id": user_id, "username": username, "points": float(points)})
            return nuked_users
    except FileNotFoundError:
        return []


# Function: Final escalation (all branches working together)
async def final_escalation(user, message):
    """
    Handles the ultimate escalation where all branches of the Gyatt_Team interact together.
    
    Args:
        user: The user being targeted.
        message: The Discord message object.
    """
    # Responses from each branch (now using FINAL_RESPONSES)
    police_response = random.choice(GAY_POLICE_FINAL_RESPONSES)
    army_response = random.choice(GAY_ARMY_FINAL_RESPONSES)
    navy_response = random.choice(GAYVIE_FINAL_RESPONSES)
    airforce_response = random.choice(GAY_AIRFORCE_FINAL_RESPONSES)

    # Coordinated final attack messages
    await message.channel.send(f"🚨 Gay Police: {police_response} {user.mention}")
    await asyncio.sleep(1)  # Add slight delay for dramatic effect
    await message.channel.send(f"⚔️ Gay Army: {army_response} {user.mention}")
    await asyncio.sleep(1)
    await message.channel.send(f"⚓ Gay Navy: {navy_response} {user.mention}")
    await asyncio.sleep(1)
    await message.channel.send(f"✈️ Gay Airforce: {airforce_response} {user.mention}")

    # Final bombastic declaration and log the user as nuked!
    await asyncio.sleep(1)
    await message.channel.send(
        f"🌈 ALL BRANCHES DEPLOYED! The Gyatt_Team has unleashed its full power on {user.mention}! "
        f"Susness eradicated! 💥"
    )

    # Log the user as nuked in the record file (using their total points from police records)
    police_records = load_police_records()
    total_points = police_records.get(str(user.id), 0)
    log_nuked_user(user.id, user.name, total_points)


# Slash Command: Check if a specific user has been nuked (/Gyatt Team @user or /Gyatt Team Nuked)
@slash.slash(name="GyattTeam", description="Check if a user has been nuked or show all nuked users.")
async def gyatt_team(ctx: SlashContext, option: str):
    """
    Handles slash commands to check if a user has been nuked or to show all nuked users.
    
    Args:
        ctx: The context of the slash command.
        option: Either an @user mention or "Nuked" to show all records.
    """
    if option.lower() == "nuked":
        # Show all nuked users
        nuked_users = load_nuked_users()
        if not nuked_users:
            await ctx.send("No one has been nuked yet! 🌈")
            return

        response = "**List of Nuked Users:**\n"
        for user in nuked_users:
            response += f"- **{user['username']}** (ID: {user['id']}, Points: {user['points']:.2f})\n"
        await ctx.send(response)

    else:
        # Check if a specific user has been nuked (option should be an @mention)
        target_user_id = option.strip("<@!>")
        nuked_users = load_nuked_users()
        for user in nuked_users:
            if user["id"] == target_user_id:
                await ctx.send(
                    f"**{user['username']}** has been nuked by the Gyatt_Team! Total Points: {user['points']:.2f} 🌈"
                )
                return

        await ctx.send("That user has not been nuked yet! 🚨")


# Slash Command: Add a new sus phrase dynamically (/GyattTeamAdd "comment" tally value)
@slash.slash(name="GyattTeamAdd", description="Add a new sus phrase to the library with a tally value.")
async def gyatt_team_add(ctx: SlashContext, comment: str, tally: float):
    """
    Adds a new sus phrase to the library dynamically.
    
    Args:
        ctx: The context of the slash command.
        comment: The sus phrase to be added.
        tally: The point value for the sus phrase (must be between 0.1 and 15).
    """
    # Validate tally value
    if tally <= 0 or tally > 15:
        await ctx.send("🚨 Invalid tally value! It must be between 0.1 and 15.", hidden=True)
        return

    # Load existing sus phrases
    try:
        from library.sus_phrases import SUS_PHRASES
    except ImportError:
        await ctx.send("🚨 Failed to load sus phrases! Please check your configuration.", hidden=True)
        return

    # Check if the phrase already exists
    if comment.lower() in SUS_PHRASES:
        await ctx.send(f"🚨 The phrase '{comment}' already exists in the library!", hidden=True)
        return

    # Add the new phrase to SUS_PHRASES dynamically and update file content!
    SUS_PHRASES[comment.lower()] = tally

    try:
        with open("library/sus_phrases.py", "w") as f:
            f.write("SUS_PHRASES = {\n")
            for phrase, value in SUS_PHRASES.items():
                f.write(f'    "{phrase}": {value},\n')
            f.write("}\n")
        
        await ctx.send(f"✅ Successfully added '{comment}' with a tally of {tally} to the sus library!")
    
    except Exception as e:
        await ctx.send(f"🚨 Failed to update sus phrases file: {e}", hidden=True)


# Event: On Ready (Bot Startup)
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


# Event: On Message (Message Handling)
@bot.event
async def on_message(message):
    # Ignore messages from the bot itself or empty messages
    if message.author == bot.user or not message.content.strip():
        return

    # Check for sus phrases and calculate susness score (0.1–15 range per phrase)
    sus_score = calculate_susness(message.content)

    # If there's any susness detected, escalate and respond accordingly
    if sus_score > 0:
        await escalate_and_respond(message.author, message, sus_score)


# Run the bot using the token from environment variables (GitHub Secrets or .env file)
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if DISCORD_BOT_TOKEN is None:
    raise ValueError("DISCORD_BOT_TOKEN not found in environment variables.")
bot.run(DISCORD_BOT_TOKEN)
    
