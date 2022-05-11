from collections import defaultdict
import colorsys
import math
import numpy as np
import pygame
from typing import Sequence, Callable, Union

from Game.environment import Environment


class Game:
    def __init__(self, display, size: tuple, game_mode: str = 'field', border: bool = False, snake_speed: float = 1,
                 block_size: int = 5, max_fps: int = 180):
        super().__init__()

        # Store arguments
        self._display = display
        self.snake_speed = max(snake_speed, 0.1)
        self.block_size = block_size
        self.game_size = size
        self.max_fps = max_fps

        # Init attributes
        self.clock = pygame.time.Clock()
        self.environment = Environment(game_mode=game_mode, width=self.game_size[0], height=self.game_size[1],
                                       border=border)
        self.game_over = True
        self.closing = False

        # Set styles
        self.font_style = pygame.font.SysFont("bahnschrift", 25)
        colors = {
            'black': (0, 0, 0),
            'blue': (50, 153, 213),
            'green': (0, 255, 0),
            'light blue': (154, 205, 255),
            'light green': (180, 240, 180),
            'light grey': (235, 235, 235),
            'red': (213, 50, 80),
            'white': (255, 255, 255),
            'yellow': (255, 255, 102),
        }
        self.colors = defaultdict(lambda: (0, 0, 0), **colors)
        self._snake_colors = {}

        # Set manual game commands ("nesw" for each player)
        self._received_commands = {k: None for k in range(4)}
        self._manual_commands = {
            pygame.K_UP: (0, 0), pygame.K_RIGHT: (0, 1), pygame.K_DOWN: (0, 2), pygame.K_LEFT: (0, 3),
            pygame.K_w: (1, 0), pygame.K_d: (1, 1), pygame.K_s: (1, 2), pygame.K_a: (1, 3),
            pygame.K_i: (2, 0), pygame.K_l: (2, 1), pygame.K_k: (2, 2), pygame.K_j: (2, 3),
            pygame.K_KP8: (3, 0), pygame.K_KP6: (3, 1), pygame.K_KP5: (3, 2), pygame.K_KP4: (3, 3),
        }

    @staticmethod
    def __get_distant_colors(n: int, form: str = 'rgb') -> Sequence[Sequence]:
        """
        Get a list of colors that are as distant as possible

        Parameters
        ----------
        n : int
            Number of colors to create.
        form : str, optional
            Format of the output color list. Admissible formats are:
                'rgb' or 'rgb_float' -> float rgb values between 0 and 1
                'rgb_int' -> int rgb values between 0 and 255
                'hls' -> float hls values between 0 and 1
                'hex' -> hexadecimal rgb color strings
            The default is 'rgb'.

        Returns
        -------
        colors : Sequence[Sequence]
            Sequence of colors in the specified format.

        """

        def rgb2hex(rgb: tuple) -> str:
            """
            Translates a rgb tuple of int to hex color

            Parameters
            ----------
            rgb : tuple
                Tuple reporting color in (R, G, B) format.

            Returns
            -------
            h : str
                String reporting color in hex format.

            """
            return "#%02x%02x%02x" % tuple(rgb)

        # Get number of luminosities and hues
        n_l = int(math.log(n, 4)) + 1
        n_h = int(np.ceil(n / n_l))

        # Get color list
        hls_colors = []
        for ll in range(n_l):
            th = ll / (n_l * (n_h + 1))
            hls_colors.extend([(hh + th if hh < (1 - th) else hh + th - 1, (ll + 1) / (n_l + 1), 1)
                               for hh in np.linspace(0, 1, n_h + 1)[:-1]])

        hls_colors = hls_colors[:n]
        colors = [colorsys.hls_to_rgb(h, l, s) for h, l, s in hls_colors]
        int_colors = [tuple(int(cc * 255) for cc in c) for c in colors]

        # Prepare output list
        if form == 'rgb_int':
            return int_colors
        if form == 'hls':
            return hls_colors
        if form == 'hex':
            return [rgb2hex(c) for c in int_colors]

        return colors

    def show_message(self, text: str, color: tuple = (0, 0, 0), font_style=None, pos: Sequence = None,
                     anchor: str = 'ensw'):
        # Normalize inputs
        if font_style is None:
            font_style = self.font_style
        anchor = ''.join(sorted(set(anchor)))

        # Set position
        if pos is None:
            pos = [None, None]
        if pos[0] is None:
            pos[0] = self._display.get_width() // 2
        if pos[1] is None:
            pos[1] = self._display.get_height() // 2

        # Display message
        msg = font_style.render(text, True, color)
        msg_rect = msg.get_rect()
        msg_rect.center = pos
        if anchor == 'ensw':
            pass
        elif anchor == 'e':
            msg_rect.centerx += msg_rect.width // 2
        elif anchor == 'n':
            msg_rect.centery += msg_rect.height // 2
        elif anchor == 's':
            msg_rect.centery -= msg_rect.height // 2
        elif anchor == 'w':
            msg_rect.centerx -= msg_rect.width // 2
        elif anchor == 'en':
            msg_rect.centerx += msg_rect.width // 2
            msg_rect.centery += msg_rect.height // 2
        elif anchor == 'nw':
            msg_rect.centerx -= msg_rect.width // 2
            msg_rect.centery += msg_rect.height // 2
        elif anchor == 'es':
            msg_rect.centerx += msg_rect.width // 2
            msg_rect.centery -= msg_rect.height // 2
        elif anchor == 'sw':
            msg_rect.centerx -= msg_rect.width // 2
            msg_rect.centery -= msg_rect.height // 2
        self._display.blit(msg, msg_rect)

    def play(self, move_snakes: Sequence[Callable], len_snakes: Union[Sequence[int], int] = 3, **kwargs):
        # Init attributes
        self.game_over = True
        self.closing = False
        num_snakes = len(move_snakes)
        self._snake_colors = {num: color for num, color in enumerate(self.__get_distant_colors(num_snakes, 'rgb_int'))}

        # Predispose time counter
        tick_time = 0

        # Main game loop
        while not self.closing:
            # Show text and scores while waiting for player
            if self.game_over:
                self._display.fill(self.colors['light blue'])
                for ii, score in enumerate(self.environment.get_scores()):
                    self.show_message(f"Player {ii} score: {score}", self._snake_colors[ii],
                                      pos=(5, 5 + 30*ii), anchor='ne')
                self.show_message("Press P-Play Again or Q-Quit", self.colors['black'])
                pygame.display.update()

                # Wait for user interaction
                for event in pygame.event.get():
                    # Quit the game if required
                    if event.type == pygame.QUIT:
                        self.game_over = True
                        self.closing = True

                    # Get key press
                    if event.type == pygame.KEYDOWN:
                        # Quit the game
                        if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                            self.game_over = False
                            self.closing = True

                        # Restart the game
                        if event.key == pygame.K_p or event.key == pygame.K_RETURN:
                            self.game_over = False
                            self.closing = False
                            self.environment.setup(move_snakes=move_snakes, len_snakes=len_snakes, pos_snakes=None,
                                                   **kwargs)
                            tick_time = pygame.time.get_ticks() - (1 / self.snake_speed * 1000)

            # Play the game
            else:
                # TODO add no-display mode

                # TODO display scores in real time

                # Get keyboard events
                for event in pygame.event.get():
                    # Quit the game if required
                    if event.type == pygame.QUIT:
                        self.game_over = True
                        self.closing = True
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.game_over = True
                    if event.type == pygame.KEYDOWN:
                        if event.key in self._manual_commands:
                            idx, direction = self._manual_commands[event.key]
                            if move_snakes[idx] is None:
                                self._received_commands[idx] = direction

                # Update screen at snakes speed
                if pygame.time.get_ticks() - tick_time > (1 / self.snake_speed * 1000):
                    tick_time = pygame.time.get_ticks()

                    # Rotate snakes for manual control
                    self.environment.send_commands(self._received_commands)
                    self._received_commands = {k: None for k in self._received_commands.keys()}

                    # Do one game step
                    self.environment.update()

                    # Check if game has ended
                    if self.environment.game_over():
                        self.game_over = True

                    # Update display
                    self._display.fill(self.colors['black'])
                    self.__update_display()

                # Wait clock
                self.clock.tick(self.max_fps)

        # Quit the game
        pygame.quit()

    def __update_display(self):
        # Get current game field
        game_field = self.environment.game_field

        # Set threshold to add a 1 pixel border
        th = 5

        # Map colors
        colormap = {1: self.colors['white'], -1: self.colors['red']}
        colormap.update({k+2: v for k, v in self._snake_colors.items()})

        # Update display accordingly
        for y, x in zip(*np.where(game_field)):
            label = game_field[y, x]
            if label not in colormap:
                continue
            pygame.draw.rect(self._display, colormap[label],
                             [x * self.block_size + (self.block_size > th),
                              y * self.block_size + (self.block_size > th),
                              self.block_size - (self.block_size > th) * 2,
                              self.block_size - (self.block_size > th) * 2])

        # Update display
        pygame.display.update()
