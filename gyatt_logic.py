import random
import spacy  # Import spaCy for NLP
import discord
import asyncio
import calculations   # Dynamic multiplier system
import library.sus_phrases   # Import sus phrases dynamically
import library.gay_police_responses
import library.gay_army_responses 
import library.gayvie_responses 
import library.gay_airforce_responses 
import bots.gay_police 
import bots.gay_army 
import bots.gayvie 
import bots.gay_airforce 

def add_sus_phrase(phrase, score):
    """Adds a new sus phrase to the SUS_PHRASES dictionary."""
    library.sus_phrases.SUS_PHRASES[phrase] = score
    return f"Phrase '{phrase}' added successfully with score {score}!"

def remove_sus_phrase(phrase):
    """Removes a sus phrase from the SUS_PHRASES dictionary."""
    if phrase in library.sus_phrases.SUS_PHRASES:
        del library.sus_phrases.SUS_PHRASES[phrase]
        return f"Phrase '{phrase}' removed successfully!"
    return f"Phrase '{phrase}' not found!"

def list_sus_phrases():
    """Returns the current list of sus phrases."""
    return "\n".join([f"{phrase}: {score}" for phrase, score in library.sus_phrases.SUS_PHRASES.items()])

# Load spaCy's medium-sized English model
nlp = spacy.load("en_core_web_md")

# Persistent tally tracking files
POLICE_RECORD_FILE = "police_record.txt"
NUKED_RECORD_FILE = "nuked.py"

# Thresholds for escalation
GAY_POLICE_THRESHOLD = 5
GAY_ARMY_NAVY_THRESHOLD = 10
GAY_AIRFORCE_THRESHOLD = 15


### Susness Calculation ###
def calculate_susness(message):
    """
    Calculates susness using semantic similarity with spaCy.
    Handles long messages by splitting them into sentences.
    Args:
        message (str): The user's input message.
    Returns:
        float: The total susness score based on semantic similarity.
    """
    # Split the message into sentences using spaCy
    user_doc = nlp(message.lower())
    sentences = [sent.text for sent in user_doc.sents]  # Extract sentences
    sus_score = 0

    # Analyze each sentence for susness
    for sentence in sentences:
        sentence_doc = nlp(sentence)
        sentence_score = 0

        # Compare the sentence with each phrase in SUS_PHRASES
        for phrase, score in library.sus_phrases.SUS_PHRASES.items():
            phrase_doc = nlp(phrase.lower())
            similarity = sentence_doc.similarity(phrase_doc)  # Semantic similarity calculation
            if similarity >= 0.8:  # Threshold for semantic similarity (adjustable)
                sentence_score = max(sentence_score, score)  # Take the highest matching score

        # Add the highest score from this sentence to the total score
        sus_score += sentence_score

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

        # Check if the branch name exists in the image paths
        if branch_name not in image_paths:
            print(f"Branch '{branch_name}' does not have any associated images.")
            return

        # Randomly select an image for the given branch
        selected_image = random.choice(image_paths[branch_name])

        # Send the image as an attachment
        file = discord.File(selected_image)
        await message.channel.send(file=file)

    except FileNotFoundError:
        print(f"Image file not found for branch '{branch_name}'. Ensure all images are in the correct directory.")
    except Exception as e:
        print(f"Failed to send image for {branch_name}: {e}")
        
