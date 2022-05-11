import numpy as np
import random
from typing import Union, Callable, Sequence, Dict

import game_rules
from Snake.snake import Snake


class Environment:
    def __init__(self, game_mode: str = 'field', width: int = 10, height: int = 10, border: bool = False):
        super().__init__()

        # Init attributes
        self.__game_mode = game_mode
        self._width = width
        self._height = height
        self.__border = border
        self.__snakes: Dict[int, Snake] = {}
        self._food_x = self._food_y = 0
        self.game_properties: dict = {}
        self.__rotation_dir: Sequence[str] = ('n', 'e', 's', 'w')
        self.__snake_num_offset: int = 2

        # Init field matrix
        self._field = np.zeros((width - self.__border*2, height - self.__border*2), dtype=bool)
        if self.__border:
            self._field = np.pad(self._field, ((1, 1), (1, 1)), constant_values=True)

    @property
    def field(self):
        return self._field

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def game_field(self):
        # Get empty field
        field = self.field.astype('int8') * 1

        # Get food position
        field[self._food_y, self._food_x] = -1

        # Get snakes positions
        for num, snake in self.__snakes.items():
            if snake.alive or self.game_properties.get('keep_corpse', False):
                for pos in snake.body:
                    field[pos[1], pos[0]] = num if snake.alive else 1

        return field

    def reset(self):
        # Reset field matrix
        if self.__border:
            self._field[1:-2, 1:-2] = False
        else:
            self._field[:] = False

    def __put_food(self):
        # Get current game field
        game_field = self.game_field > 0
        updated_game_field = game_field.copy()

        # Position food
        food_x = food_y = 0
        while np.sum(np.bitwise_xor(game_field, updated_game_field)) == 0:
            food_x = random.randint(0, game_field.shape[1]-1)
            food_y = random.randint(0, game_field.shape[0]-1)
            updated_game_field[food_y, food_x] = True

        # Update field
        self._food_x, self._food_y = food_x, food_y

    def setup(self, move_snakes: Sequence[Callable] = (), len_snakes: Union[Sequence[int], int] = 3,
              pos_snakes: Union[Sequence[Union[None, tuple]], None] = None, food_score: int = 1, kill_score: int = 5,
              recognize_enemies: bool = False, keep_corpse: bool = False):
        # Store game properties
        self.game_properties = {
            'food_score': food_score,
            'kill_score': kill_score,
            'recognize_enemies': recognize_enemies,
            'keep_corpse': keep_corpse,
        }

        # Normalize inputs
        num_snakes = len(move_snakes)
        len_snakes = tuple([len_snakes]*num_snakes if isinstance(len_snakes, int) else len_snakes)
        pos_snakes = tuple([pos_snakes] * num_snakes if pos_snakes is None else pos_snakes)
        assert (len(len_snakes) == num_snakes) and (len(pos_snakes) == num_snakes), \
            f"Invalid number of snakes. Expected: {num_snakes}, got {len(len_snakes)} and {len(pos_snakes)}."

        # Put food
        self.__put_food()

        # Clear current snakes
        self.__snakes = {}

        # Initialize snakes
        for num, (move_snake, len_snake, pos_snake) in enumerate(zip(move_snakes, len_snakes, pos_snakes)):
            if pos_snake is None:
                pos_snake = self._food_x, self._food_y
                self.__put_food()
            snake = Snake(pos=[pos_snake], length=len_snake)
            snake.set_move_method(self.__game_mode, move_snake)
            self.__snakes[num+self.__snake_num_offset] = snake

    def send_commands(self, commands: dict):
        # Update snakes' direction based on commands
        for num, snake in self.__snakes.items():
            direction = commands.get(num-self.__snake_num_offset, None)
            if direction is not None:
                snake.direction = 'nesw'[direction % 4]

    def update(self):
        # Store collisions
        collisions = []

        # Move snakes
        eat = False
        for snake in self.__snakes.values():
            if not snake.alive:
                continue

            # Prepare shared arguments for move function
            food_pos = np.array([self._food_x - snake.x, self._food_y - snake.y])
            body = np.array(snake.body) - snake.head
            num_rotations = 'nwse'.index(snake.direction)
            food_pos = self.__rotate(food_pos * [1, -1], num_rotations)
            body = self.__rotate(body * [1, -1], num_rotations)
            args = (
                self.__game_mode,
                food_pos if self.__border else
                (food_pos[0] if abs(food_pos[0]) <= self.width//2 else self.width//2 - food_pos[0],
                 food_pos[1] if abs(food_pos[1]) <= self.height//2 else self.height//2 - food_pos[1]),
                body,
            )

            # Move snake
            if self.__game_mode == game_rules.GameModes.field:
                game_field = np.clip(self.game_field, 0,
                                     self.__snake_num_offset if self.game_properties.get('recognize_enemies', False) else None)
                move = snake.move(*args, game_field)
            elif self.__game_mode == game_rules.GameModes.head:
                # TODO
                move = snake.move(*args, self.game_field)
            elif self.__game_mode == game_rules.GameModes.body:
                # TODO
                move = snake.move(*args, self.game_field)
            else:
                move = snake.move(*args)

            # Update head
            snake.direction = self.__rotation_dir[(self.__rotation_dir.index(snake.direction) + move) % 4]
            if snake.direction == 'n':
                head_add = (0, -1)
            elif snake.direction == 'e':
                head_add = (1, 0)
            elif snake.direction == 's':
                head_add = (0, 1)
            elif snake.direction == 'w':
                head_add = (-1, 0)
            else:
                raise ValueError(f"Snake direction {snake.direction} not understood.")
            head = (snake.head[0] + head_add[0]) % self._width, (snake.head[1] + head_add[1]) % self._height

            # Check for food eat
            if head == (self._food_x, self._food_y):
                snake.len += 1
                snake.score += self.game_properties.get('food_score', 1)
                eat = True

            # Check for collision
            collision = snake.check_collision(self.game_field, head)
            if collision > 0:
                snake.alive = False
                collisions.append(collision)

            # Kill snakes due to head-to-head collision
            if collision in self.__snakes and self.__snakes[collision].head == snake.head:
                self.__snakes[collision].alive = False

            # Perform movement
            snake.update(head)

        # Give points for collisions
        for num, snake in self.__snakes.items():
            if snake.alive:
                snake.score += self.game_properties.get('kill_score', 5) * collisions.count(num)

        # Update food position
        if eat:
            self.__put_food()

    @staticmethod
    def __rotate(vect, k):
        rot = np.array([[np.cos(np.pi/2 * k), -np.sin(np.pi/2 * k)], [np.sin(np.pi/2 * k), np.cos(np.pi/2 * k)]])
        return np.round(np.array(vect).dot(rot)).astype('int32')

    def game_over(self):
        return all(not snake.alive for snake in self.__snakes.values())

    def get_scores(self):
        return [snake.score for snake in self.__snakes.values()]
