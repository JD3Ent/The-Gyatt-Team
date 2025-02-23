import discord
import os
import random
import asyncio
from dotenv import load_dotenv  # For loading environment variables
from library.sus_phrases import calculate_susness
from library.gay_police_responses import GAY_POLICE_RESPONSES, GAY_POLICE_ESCALATION_RESPONSES
from library.gay_army_responses import GAY_ARMY_RESPONSES
from library.gayvie_responses import GAYVIE_RESPONSES
from library.gay_airforce_responses import GAY_AIRFORCE_RESPONSES
from library.special_treatment import SPECIAL_TREATMENT_RESPONSES

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
                records[user_id] = int(tally)
            return records
    except FileNotFoundError:
        return {}


# Helper function: Save police records to file
def save_police_records(records):
    with open(POLICE_RECORD_FILE, "w") as f:
        for user_id, tally in records.items():
            f.write(f"{user_id}:{tally}\n")


# Helper function: Get top 10 sus users (only if there’s enough data)
def get_top_sus_users(records):
    # Only calculate top 10 if there are at least 10 users and each has at least 50 points
    if len(records) >= 10 and all(tally >= 50 for tally in records.values()):
        return sorted(records.items(), key=lambda x: x[1], reverse=True)[:10]
    return []


# Function: Handle escalation and dynamic replies
async def escalate_and_respond(user, message, sus_score):
    global active_interactions

    # Check if user is in active interactions
    if user.id not in active_interactions:
        active_interactions[user.id] = {"sus_score": 0, "timeout": None}

    # Update sus score for this interaction
    active_interactions[user.id]["sus_score"] += sus_score

    # Determine response level based on total sus score in this interaction
    total_sus_score = active_interactions[user.id]["sus_score"]

    if total_sus_score < GAY_POLICE_THRESHOLD:
        response = random.choice(GAY_POLICE_RESPONSES)
        await message.channel.send(f"{response} {user.mention}")
    elif total_sus_score < GAY_ARMY_NAVY_THRESHOLD:
        response = random.choice(GAY_ARMY_RESPONSES)
        await message.channel.send(f"🚨 Gay Army has been called! {response} {user.mention}")
    elif total_sus_score < GAY_AIRFORCE_THRESHOLD:
        navy_response = random.choice(GAYVIE_RESPONSES)
        await message.channel.send(f"⚓ Gay Navy incoming! {navy_response} {user.mention}")
    else:
        airforce_response = random.choice(GAY_AIRFORCE_RESPONSES)
        await message.channel.send(f"✈️ Gay Airforce deployed! {airforce_response} {user.mention}")

    # Add user to police record if they aren't already there and increment their tally
    police_records = load_police_records()
    if str(user.id) not in police_records:
        police_records[str(user.id)] = 0

    police_records[str(user.id)] += sus_score

    # Save updated police records back to file
    save_police_records(police_records)

    # Check if user is in top 10 sus users and give special treatment if they are (only if enough data exists)
    top_sus_users = get_top_sus_users(police_records)
    if top_sus_users and str(user.id) in dict(top_sus_users):
        special_response = random.choice(SPECIAL_TREATMENT_RESPONSES)
        await message.channel.send(
            f"🔥 {user.mention}, you're one of our top 10 most sus users! {special_response}"
        )

    # Reset timeout for ending the interaction after inactivity
    if active_interactions[user.id]["timeout"]:
        active_interactions[user.id]["timeout"].cancel()

    active_interactions[user.id]["timeout"] = asyncio.create_task(end_interaction_after_timeout(user))


# Function: End interaction after timeout period (if no response from user)
async def end_interaction_after_timeout(user):
    global active_interactions

    await asyncio.sleep(INTERACTION_TIMEOUT)

    if user.id in active_interactions:
        del active_interactions[user.id]
        print(f"Interaction with {user.name} ended due to timeout.")


# Event: On Ready (Bot Startup)
@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


# Event: On Message (Message Handling)
@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Check for sus phrases and calculate susness score
    sus_score = calculate_susness(message.content)

    # If there's any susness detected, escalate and respond accordingly
    if sus_score > 0:
        await escalate_and_respond(message.author, message, sus_score)


# Run the bot using the token from environment variables (GitHub Secrets or .env file)
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if DISCORD_BOT_TOKEN is None:
    raise ValueError("DISCORD_BOT_TOKEN not found in environment variables.")
client.run(DISCORD_BOT_TOKEN)
  
