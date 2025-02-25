def calculate_final_sus_points(current_sus_points, total_sus_points_on_record):
    """
    Dynamically calculates the final sus points to add to a user's total tally.

    Args:
        current_sus_points (float): The total sus points accumulated during the current conversation.
        total_sus_points_on_record (float): The user's existing total sus points from the police record.

    Returns:
        float: The final calculated sus points to add to the user's total tally.
    """
    # If no points on record, initialize as 1
    if total_sus_points_on_record is None:
        total_sus_points_on_record = 1
    # Calculate final sus points with dynamic multiplier
    final_sus_points = current_sus_points * total_sus_points_on_record
    # Return the calculated value
    return final_sus_points
