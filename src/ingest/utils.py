import math


def percentile_sorted(data: list, perc: int):
    size = len(data)
    return data[int(math.ceil((size * perc) / 100)) - 1]
