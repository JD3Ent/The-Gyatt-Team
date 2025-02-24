import random
from library.gay_police_responses import (
    GAY_POLICE_RESPONSES,
    GAY_POLICE_ESCALATION_RESPONSES,
    GAY_POLICE_FINAL_RESPONSES,
)
from calculations import calculate_final_sus_points
from gyatt_team import load_police_records, save_police_records, log_nuked_user


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
        await message.channel.send(f"🚨 {response} {user.mention}")
        interaction_data["reply_count"] = 1  # Increment reply count for tracking
    else:
        # Follow-up interaction: Analyze user's reply and escalate if necessary
        user_reply = message.content.lower()

        # Check for "surrender-like" responses
        if any(phrase in user_reply for phrase in ["i give up", "you win", "i surrender"]):
            final_response = random.choice(GAY_POLICE_FINAL_RESPONSES)
            await message.channel.send(f"🚔 {final_response} {user.mention}")
            return

        # If the user continues to act sus, escalate with a harsher response
        if sus_score >= 5:  # Example threshold for escalation
            escalation_response = random.choice(GAY_POLICE_ESCALATION_RESPONSES)
            await message.channel.send(f"🚔 {escalation_response} {user.mention}")
            interaction_data["reply_count"] += 1  # Increment reply count for further tracking

            # If it gets out of hand, signal for an all-out arrest
            if sus_score >= 10:
                await final_police_action(user, message)  # Trigger final escalation logic


async def final_police_action(user, message):
    """
    Handles the final escalation logic specifically for the Gay Police.

    Args:
        user: The user being targeted.
        message: The Discord message object.
    """
    # Final response from the Gay Police
    final_response = random.choice(GAY_POLICE_FINAL_RESPONSES)
    await message.channel.send(f"🚨 FINAL WARNING: {final_response} {user.mention}")

    # Update police records and log as nuked
    police_records = load_police_records()
    total_points = police_records.get(str(user.id), 0)

    # Log nuked user with updated points
    log_nuked_user(user.id, user.name, total_points)

    # Save updated police records back to file (if needed)
    save_police_records(police_records)
    
