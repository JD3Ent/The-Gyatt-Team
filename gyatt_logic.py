import random
import spacy  # Import spaCy for NLP
import discord
import asyncio
from calculations import calculate_final_sus_points  # Dynamic multiplier system
from library.gay_police_responses import GAY_POLICE_FINAL_RESPONSES, GAY_POLICE_ESCALATION_RESPONSES
from library.gay_army_responses import GAY_ARMY_FINAL_RESPONSES, GAY_ARMY_ESCALATION_RESPONSES
from library.gayvie_responses import GAYVIE_FINAL_RESPONSES, GAYVIE_ESCALATION_RESPONSES
from library.gay_airforce_responses import GAY_AIRFORCE_FINAL_RESPONSES, GAY_AIRFORCE_ESCALATION_RESPONSES
from bots.gay_police import gay_police_interaction
from bots.gay_army import gay_army_interaction
from bots.gayvie import gayvie_interaction
from bots.gay_airforce import gay_airforce_interaction

# Load spaCy's medium-sized English model
nlp = spacy.load("en_core_web_md")

# Persistent tally tracking files
POLICE_RECORD_FILE = "police_record.txt"
NUKED_RECORD_FILE = "nuked.py"

# SUS_PHRASES dictionary (can be dynamically updated via slash commands)
SUS_PHRASES = {
    "I like your hair": 0.5,
    "you're cute": 1.5,
    "come here daddy": 4.5,
    "rail me daddy": 13,
}

# Thresholds for escalation
GAY_POLICE_THRESHOLD = 5
GAY_ARMY_NAVY_THRESHOLD = 10
GAY_AIRFORCE_THRESHOLD = 15


### Susness Calculation ###
def calculate_susness(message):
    """
    Calculates susness using semantic similarity with spaCy.

    Args:
        message (str): The user's input message.

    Returns:
        float: The highest susness score based on semantic similarity.
    """
    user_doc = nlp(message.lower())
    sus_score = 0

    for phrase, score in SUS_PHRASES.items():
        phrase_doc = nlp(phrase.lower())
        similarity = user_doc.similarity(phrase_doc)  # Semantic similarity calculation

        if similarity >= 0.8:  # Threshold for semantic similarity (adjustable)
            sus_score = max(sus_score, score)  # Take the highest matching score

    return sus_score


### Escalation Logic ###
async def escalate_and_respond(user, message, sus_score):
    """
    Handles escalation and dynamic replies based on susness score.
    
    Args:
        user: The Discord user object.
        message: The Discord message object.
        sus_score: Calculated susness score.
    """
    global active_interactions

    # Check if user is in active interactions
    if user.id not in active_interactions:
        active_interactions[user.id] = {"sus_score": 0, "timeout": None}

    # Update sus score for this interaction (with multiplier logic)
    final_sus_score = calculate_final_sus_points(sus_score)
    active_interactions[user.id]["sus_score"] += final_sus_score

    total_sus_score = active_interactions[user.id]["sus_score"]

    # Determine response level based on total sus score in this interaction
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


### Image Handling ###
async def send_image(message, branch_name):
    """
    Sends an image corresponding to the branch triggering the interaction.

    Args:
        message: The Discord message object.
        branch_name: The name of the branch (e.g., 'gay_police', 'gay_army').
    """
    
