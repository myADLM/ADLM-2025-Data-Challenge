import math


def seconds_to_timestamp(seconds: float) -> str:
    """Converts a given time in seconds to a human-readable timestamp format.

    Args:
        seconds (float): The time duration in seconds.

    Returns:
        str: A formatted string representing the time in the format "HHhMMmSSs",
             where HH is hours, MM is minutes, and SS is seconds, all zero-padded
             to two digits.
    """
    seconds = math.floor(seconds)
    second = int(seconds % 60)
    minute = int((seconds / 60) % 60)
    hour = int(seconds / (60 * 60))
    return f"{hour:02d}h{minute:02d}m{second:02d}s"
