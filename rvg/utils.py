import math


def prettify_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    step = int(math.floor(math.log(size_bytes, 1024)))
    divider = math.pow(1024, step)
    value = round(size_bytes / divider, 2)
    return f'{value} {size_name[step]}'
