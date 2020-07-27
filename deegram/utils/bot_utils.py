from typing import Union

SIZE_UNITS = ["B", "KB", "MB", "GB", "TB", "PB"]


def get_readable_file_size(size_in_bytes: Union[int, float]) -> str:
    if size_in_bytes is None:
        return "0B"
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f"{round(size_in_bytes, 2)} {SIZE_UNITS[index]}"
    except IndexError:
        return "File troppo grande."


def get_readable_time(secs: float) -> str:

    seconds = (secs % 3600) % 60
    minutes = (secs % 3600) // 60
    hours = (secs // 3600) % 24
    days = secs // 3600 // 24

    temp = []

    if days > 0:
        ris = '<b>{}</b> giorn'.format(days)
        ris += 'o' if days == 1 else 'i'
        temp.append(ris)
    if hours > 0:
        ris = '<b>{}</b> or'.format(hours)
        ris += 'a' if hours == 1 else 'e'
        temp.append(ris)
    if minutes > 0:
        ris = '<b>{}</b> minut'.format(minutes)
        ris += 'o' if minutes == 1 else 'i'
        temp.append(ris)
    if seconds > 0:
        ris = '<b>{}</b> second'.format(seconds)
        ris += 'o' if seconds == 1 else 'i'
        temp.append(ris)

    return ', '.join(temp) + '.'
