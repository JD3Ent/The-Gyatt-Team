import discord
import os
import random
import asyncio
from dotenv import load_dotenv  # For loading environment variables
from calculations import calculate_final_sus_points  # Dynamic multiplier system
from library.sus_phrases import calculate_susness
from library.gay_police_responses import GAY_POLICE_FINAL_RESPONSES import GAY_POLICE_FINAL_RESPONSES
from library.gay_army_responses import GAY_ARMY_FINAL_RESPONSES import GAY_POLICE_FINAL_RESPONSES
from library.gayvie_responses import GAYVIE_FINAL_RESPONSES import 
from library.gay_airforce_responses import GAY_AIRFORCE_FINAL_RESPONSES
from bots.gay_police import gay_police_interaction
from bots.gay_army import gay_army_interaction
from bots.gayvie import gayvie_interaction
from bots.gay_airforce import gay_airforce_interaction

# Load environment variables (for local dev)
load_dotenv()

# Discord bot intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

# Persistent tally tracking file
POLICE_RECORD_FILE = "police_record.txt"

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


# Function: Handle escalation and dynamic replies
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


# Function: Handle escalation to backup (Gay Army/Navy)
async def escalate_to_backup(user, message):
    navy_response = random.choice(GAYVIE_ESCALATION_RESPONSES)
    army_response = random.choice(GAY_ARMY_ESCALATION_RESPONSES)
    
    await message.channel.send(f"⚓ Gay Navy incoming! {navy_response} {user.mention}")
    await message.channel.send(f"🚨 Gay Army deployed! {army_response} {user.mention}")


# Function: Final escalation (all branches working together)
async def final_escalation(user, message):
    """
    Handles the ultimate escalation where all branches of the Gyatt_Team interact together.
    
    Args:
        user: The user being targeted.
        message: The Discord message object.
    """
    # Responses from each branch
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

    # Final bombastic declaration
    await asyncio.sleep(1)
    await message.channel.send(
        f"🌈 ALL BRANCHES DEPLOYED! The Gyatt_Team has unleashed its full power on {user.mention}! "
        f"Susness eradicated! 💥"
    )


# Function: End interaction after timeout period (if no response from user)
async def end_interaction_after_timeout(user):
    global active_interactions

    # Wait for 60 seconds of inactivity
    await asyncio.sleep(INTERACTION_TIMEOUT)

    # Check if user is still in active interactions
    if user.id in active_interactions:
        # Get the user's current conversation sus score
        current_sus_points = active_interactions[user.id]["sus_score"]

        # Load police records from file
        police_records = load_police_records()

        # Get the user's existing total tally from police records (default to 0 if not found)
        total_sus_points_on_record = police_records.get(str(user.id), 0)

        # Calculate the final sus points using the multiplier system
        final_sus_points = calculate_final_sus_points(current_sus_points, total_sus_points_on_record)

        # Update the user's total tally in police records
        police_records[str(user.id)] = total_sus_points_on_record + final_sus_points

        # Save updated records back to file
        save_police_records(police_records)

        # Remove user from active interactions
        del active_interactions[user.id]

        print(f"Interaction with {user.name} ended due to timeout. Final sus points added: {final_sus_points:.2f}")


# Event: On Ready (Bot Startup)
@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


# Event: On Message (Message Handling)
@client.event
async def on_message(message):
    # Ignore messages from the bot itself or empty messages
    if message.author == client.user or not message.content.strip():
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
client.run(DISCORD_BOT_TOKEN)
