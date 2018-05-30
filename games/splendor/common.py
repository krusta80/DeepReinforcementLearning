import functools
import json


# Common utilities

def convert_cost(cost):
    return functools.reduce(lambda converted_cost, stack_size: (converted_cost << 3) + stack_size, cost)


def translate_chip_count(x):
    in_english = ""
    colors = ["B", "G", "R", "W", "b", "*"]
    for i in range(0, 6):
        in_english += colors[i] + ": " + str(x & 7) + ",  "
        x = x >> 3
    return in_english


def get_color_index(color):
    colors = {
        "B": 0,
        "G": 1,
        "R": 2,
        "W": 3,
        "b": 4,
        "g": 5
    }
    return colors[color]


def show(obj):
    return json.JSONEncoder().encode(obj)
