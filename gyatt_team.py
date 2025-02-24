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


# Function: Send an image with the first interaction (now with multiple images per branch)
async def send_image(message, branch_name):
    """
    Sends an image corresponding to the branch triggering the interaction.

    Args:
        message: The Discord message object.
        branch_name: The name of the branch (e.g., 'gay_police', 'gay_army').
    """
    try:
        # Define file paths for each branch's images (3 images per branch)
        image_paths = {
            "gay_police": [
                "images/gay_police_1.png",
                "images/gay_police_2.png",
                "images/gay_police_3.png",
            ],
            "gay_army": [
                "images/gay_army_1.png",
                "images/gay_army_2.png",
                "images/gay_army_3.png",
            ],
            "gayvie": [
                "images/gayvie_1.png",
                "images/gayvie_2.png",
                "images/gayvie_3.png",
            ],
            "gay_airforce": [
                "images/gay_airforce_1.png",
                "images/gay_airforce_2.png",
                "images/gay_airforce_3.png",
            ],
        }

        # Randomly select an image for the given branch
        selected_image = random.choice(image_paths[branch_name])

        # Send the image as an attachment
        file = discord.File(selected_image)
        await message.channel.send(file=file)

    except Exception as e:
        print(f"Failed to send image for {branch_name}: {e}")


# Function: Handle escalation and dynamic replies (with images)
async def escalate_and_respond(user, message, sus_score):
    global active_interactions

    # Check if user is in active interactions
    if user.id not in active_interactions:
        active_interactions[user.id] = {"sus_score": 0, "timeout": None}

    # Update sus score for this interaction (no multiplier here)
    active_interactions[user.id]["sus_score"] += sus_score

    # Determine response level based on total sus score in this interaction
    total_sus_score = active_interactions[user.id]["sus_score"]

    if total_sus_score < GAY_ARMY_NAVY_THRESHOLD:
        result = await gay_police_interaction(user, message, active_interactions[user.id])
        if result == "escalate":
            await escalate_to_backup(user, message)

    elif total_sus_score < GAY_AIRFORCE_THRESHOLD:
        result = await gay_army_interaction(user, message, active_interactions[user.id])
        if result == "full_attack":
            await escalate_to_backup(user, message)
        else:
            result = await gayvie_interaction(user, message, active_interactions[user.id])
            if result == "full_assault":
                await escalate_to_backup(user, message)

    elif total_sus_score >= GAY_AIRFORCE_THRESHOLD:
        result = await gay_airforce_interaction(user, message, active_interactions[user.id])
        if result == "final_strike":
            await final_escalation(user, message)


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
