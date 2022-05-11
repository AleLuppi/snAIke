import pygame
from typing import Union

from Game.game import Game
import game_rules

# ----- Get the moving methods -----

move_snakes = (None, None)
# ----------------------------------


# Set game rules
game_mode: str = game_rules.GameModes.field  # game mode
kill_mode: str = game_rules.KillModes.die  # kill mode
food_score: int = 1  # points to eat food
kill_score: int = 5  # points to kill another snake
recognize_enemies: bool = False  # if True, each snake is able to recognize each other snake individually
keep_corpse: bool = False  # if True, dead snakes become obstacles
border: bool = False  # if True use borders, otherwise use teleportation (pac-man effect)

# Set snake params
# -------------------------
# EXAMPLE:
#
#   game_mode = 'head'
#
#   fov_head[0] = 3  fov_head_offset = 1
#              <---><->
#              - - - - - - -  ^                         - := visible field
#              - - - - - - -  | fov_head[1] = 3         H := head
#              - - - - - - -  v                         B := body
#              - - - ← H B B                            ← := snake direction
#              - - - - - - -   snake_initial_len = 3    Sx := snake x (only if recognize_enemies = True, otherwise 'S')
#              - - - - - - -
#              - S1S1 - - S2-
# -------------------------
snake_initial_len: int = 3  # initial stake length
fov_head: Union[int, tuple] = 4  # how many blocks of distance can snake see in each direction, may differ in direction
fov_head_offset: int = 0  # How many blocks to offset snake's sight in head direction
fov_body: int = 1  # how many blocks of distance can snake body sense in each direction

# Set display params
game_width: int = 50
game_height: int = 50
show_live_scores: bool = False
block_size: int = 10
snake_speed: float = 15  # how many movements per second, can be < 1

# MANUAL / HYBRID MODE
# -------------------------
# This game can be played in manual mode... just for (debug) fun!
#
# Players should use the keys:
#   player 1:   ↑ (up)      ↓ (down)    ← (left)    → (right)
#   player 2:   w (up)      s (down)    a (left)    d (right)
#   player 3:   i (up)      k (down)    j (left)    l (right)
#   player 4:   8 (up)      5 (down)    4 (left)    6 (right)   from keypad
#
# But the funniest part is... trying to beat the AI!
# You can play in hybrid mode just by activating some manual snakes along adversarial snakes.
#
# To activate manual mode, place None in move_snakes method, at the position of player who's playing, i.e.:
#   move_snakes = (None, method1, None, method2)
# activates manual players 1 and 3. Manual players from index 4 and beyond spawns snakes that go straight endlessly.
# -------------------------


def main():
    # Create the display
    pygame.init()
    display = pygame.display.set_mode((game_width * block_size + show_live_scores * 100, game_height * block_size))
    pygame.display.set_caption('AI Snake - let the best win')

    # Create and start the game
    Game(display, size=(game_width, game_height), game_mode=game_mode, border=border, snake_speed=snake_speed,
         block_size=block_size).play(move_snakes=move_snakes, len_snakes=snake_initial_len, food_score=food_score,
                                     kill_score=kill_score, recognize_enemies=recognize_enemies,
                                     keep_corpse=keep_corpse)


if __name__ == '__main__':
    main()
