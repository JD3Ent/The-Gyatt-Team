import math

def calculate_final_sus_points(current_sus_points, total_sus_points_on_record):
    """
    Dynamically calculates the final sus points using a trigonometric multiplier.

    Args:
        current_sus_points (float): The total sus points accumulated during the current conversation.
        total_sus_points_on_record (float): The user's existing total sus points from the police record.

    Returns:
        float: The final calculated sus points to add to the user's total tally.
    """

    # Handle zero total_sus_points_on_record
    if total_sus_points_on_record == 0:
        total_sus_points_on_record = 1

    # Scale total_sus_points_on_record to a suitable range for trigonometric functions
    scaled_total_sus_points = total_sus_points_on_record / 10  # Reduced divisor for faster oscillation

    # Use sine function to create an oscillating multiplier
    multiplier = 1 + math.sin(scaled_total_sus_points) ** 2 * 2 # Increased amplitude and exponential sine

    # Calculate final sus points with the oscillating multiplier
    final_sus_points = current_sus_points * multiplier

    return final_sus_points
