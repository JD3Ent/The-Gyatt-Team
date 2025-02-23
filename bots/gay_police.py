import random
from library.gay_police_responses import (
    GAY_POLICE_RESPONSES,
    GAY_POLICE_ESCALATION_RESPONSES,
    GAY_POLICE_FINAL_WARNING_RESPONSES,
)

# Function: Handle Gay Police interaction
async def gay_police_interaction(user, message, interaction_data):
    """
    Handles dynamic interactions for the Gay Police.
    Tracks user responses and escalates if necessary.
    
    Args:
        user: The user being interacted with.
        message: The Discord message object.
        interaction_data: A dictionary tracking the user's sus score and responses.
    """
    # Extract user's current sus score and number of replies
    sus_score = interaction_data["sus_score"]
    reply_count = interaction_data.get("reply_count", 0)

    # Check if this is the first interaction or a follow-up
    if reply_count == 0:
        # First interaction: Send a random Gay Police response
        response = random.choice(GAY_POLICE_RESPONSES)
        await message.channel.send(f"{response} {user.mention}")
        interaction_data["reply_count"] = 1  # Increment reply count for tracking
    else:
        # Follow-up interaction: Analyze user's reply and escalate if necessary
        user_reply = message.content.lower()

        # Check for "apology-like" responses
        if any(phrase in user_reply for phrase in ["sorry", "won't happen again", "my bad"]):
            response = random.choice(GAY_POLICE_FINAL_WARNING_RESPONSES)
            await message.channel.send(f"{response} {user.mention}")
            return

        # If the user continues to act sus, escalate with a harsher response
        if sus_score >= 5:  # Example threshold for escalation
            response = random.choice(GAY_POLICE_ESCALATION_RESPONSES)
            await message.channel.send(f"{response} {user.mention}")
            interaction_data["reply_count"] += 1  # Increment reply count for further tracking

            # If the situation gets out of hand, call for backup (Gay Army or Navy)
            if sus_score >= 10:
                await message.channel.send(
                    f"🚨 This is beyond the Gay Police's jurisdiction! Calling for backup! 🚨"
                )
                return "escalate"  # Signal to escalate to higher levels (handled in `gyatt_team.py`)
