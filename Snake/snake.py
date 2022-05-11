from random import sample
from typing import List, Callable

import game_rules


class Snake:
    def __init__(self, pos: List[tuple] = ((0, 0),), length: int = None, direction: str = None):
        super().__init__()

        # Store attributes
        self.len = length if length is not None else len(pos)
        self.body = [tuple(p) for p in pos]
        self.head = tuple(pos[0])
        self.alive = True
        self.direction = direction if direction is not None else sample('nswe', 1)[0]

        # Initialize score
        self.score = 0

    @property
    def x(self):
        return self.head[0]

    @property
    def y(self):
        return self.head[1]

    def update(self, new_head):
        # Update head and body
        self.head = tuple(new_head)
        self.body.append(self.head)
        if len(self.body) > self.len:
            del self.body[0]

    def check_collision(self, field, pos: tuple = None):
        # Check if snake collided in field
        if pos is None:
            pos = (self.x, self.y)
        return field[pos[1], pos[0]]

    def move(self, mode=game_rules.GameModes.field, /, *args, **kwargs) -> int:
        return max(min(int(self.__move(mode, *args, **kwargs)), 1), -1)

    def __move(self, mode=game_rules.GameModes.field, /, *args, **kwargs) -> int:
        # Choose the moving method
        if mode == game_rules.GameModes.field:
            return self.move_method_field(*args, **kwargs)
        elif mode == game_rules.GameModes.head:
            return self.move_method_head(*args, **kwargs)
        elif mode == game_rules.GameModes.body:
            return self.move_method_body(*args, **kwargs)
        else:
            return 0

    @ staticmethod
    def move_method_field(food, body, field) -> int:
        raise NotImplemented('Move method not implemented.')

    @staticmethod
    def move_method_head(food, body, head_field) -> int:
        raise NotImplemented('Move method not implemented.')

    @staticmethod
    def move_method_body(food, body, head_field, body_field) -> int:
        raise NotImplemented('Move method not implemented.')

    def set_move_method(self, mode: str = 'field', method: Callable = None, /):
        # Set the correct moving method
        if method is None:
            method = lambda *args, **kwargs: 0
        if mode == game_rules.GameModes.field:
            self.move_method_field = method
        elif mode == game_rules.GameModes.head:
            self.move_method_head = method
        elif mode == game_rules.GameModes.body:
            self.move_method_body = method
