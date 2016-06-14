from datetime import timedelta


def time_duration_pretty(num_seconds):
    if isinstance(num_seconds, timedelta):
        total_seconds = num_seconds.seconds
    else:
        total_seconds = int(num_seconds)
    SECS_IN_MIN = 60
    MINS_IN_HOUR = 60
    SECS_IN_HOUR = SECS_IN_MIN * MINS_IN_HOUR
    HOURS_IN_DAY = 24
    SECS_IN_DAY = SECS_IN_HOUR * HOURS_IN_DAY
    num_seconds = total_seconds % SECS_IN_MIN
    sec_unit = "second" if num_seconds == 1 else "seconds"
    current = "{0} {1}".format(num_seconds, sec_unit)
    if total_seconds < SECS_IN_MIN:
        return current
    num_minutes = (total_seconds // SECS_IN_MIN) % MINS_IN_HOUR
    min_unit = "minute" if num_minutes == 1 else "minutes"
    current = "{0} {1}, {2}".format(num_minutes, min_unit, current)
    if total_seconds < SECS_IN_HOUR:
        return current
    num_hours = (total_seconds // SECS_IN_HOUR) % HOURS_IN_DAY
    hour_unit = "hour" if num_hours == 1 else "hours"
    current = "{0} {1}, {2}".format(num_hours, hour_unit, current)
    if total_seconds < SECS_IN_DAY:
        return current
    num_days = total_seconds // SECS_IN_DAY
    day_unit = "day" if num_days == 1 else "days"
    current = "{0} {1}, {2}".format(num_days, day_unit, current)
    return current


def format_with_colors(fmt_string, *args, **kwargs):
    new_kwargs = {
        'black': '\x1b[30m',
        'red': '\x1b[31m',
        'green': '\x1b[32m',
        'yellow': '\x1b[33m',
        'blue': '\x1b[34m',
        'purple': '\x1b[35m',
        'end': '\x1b[0m',
    }
    new_kwargs.update(kwargs)
    return fmt_string.format(*args, **new_kwargs)
