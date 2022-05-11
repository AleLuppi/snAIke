import numpy as np
import random


# ----- Functions skeleton -----
def move_method_field(food, body, field) -> int:
    raise NotImplemented('Move method not implemented.')


def move_method_head(food, body, head_field) -> int:
    raise NotImplemented('Move method not implemented.')


def move_method_body(food, body, head_field, body_field) -> int:
    raise NotImplemented('Move method not implemented.')
# ------------------------------


def move_method_field_random(food, body, field) -> int:
    return random.randint(-1, 1)


def move_method_field_fuzzy(food, body, field) -> int:
    turn_prob = 0.05
    return ((x := random.random()) < turn_prob) + (x < (1-turn_prob)) - 1


def move_method_field_food_based(food, body, field) -> int:
    return np.sign(food[0])


def move_method_field_food_body_aware(food, body, field) -> int:
    move = np.sign(food[0])
    other_moves = {-1, 0, 1} - {move}
    while True:
        step = [move, 0] if move != 0 else [0, 1]
        if not (body == step).all(-1).any() or not other_moves:
            break
        move = other_moves.pop()

    return move
