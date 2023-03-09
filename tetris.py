"""
Tetris game simulation in python.
"""

import serial
import time
import numpy as np
from tqdm import tqdm

from threading import Thread
import asyncio

from sshkeyboard import listen_keyboard

import cv2

from display import CV2Display, ArduinoDisplay, MultiDisplay
from utils import Action, BLOCKS, KEYS, grid_intersection, action_slice, display_for_num

GRAVITY_TIME = 30

PAD = 2

class Tetris():
    """
    Classic Tetris on 8x8 Display
    """

    def __init__(self):
        self.reset()

    def reset(self):
        """
        Resets the Tetris grid
        """
        # current number of lines removed
        self.score = 0
        
        # 8x8 display of bytes (0 to 15 inclusive)
        self.display = np.zeros((8, 8), dtype=np.byte)
        
        # Grid stores all the stationary cells
        self.grid = np.zeros((12, 12), dtype=np.byte)
        self.grid[:, :PAD] = 1
        self.grid[:, -PAD:] = 1
        
        # Current object mask
        self.cur_obj = np.zeros((12, 12), dtype=np.byte)
        # Block type of falling object
        self.falling_type = 0
        # Top-left corner of falling object
        self.corner = np.zeros(PAD, dtype=np.byte)
        # Version of falling object (rotation)
        self.version = 0

        # Number of frames since last block fall
        self.gravity_count = 0
        
        self.spawn_piece()

    def propose_move(self, action):
        """
        Calculate transformation of mask of falling object
        after moving as specified by action

        :param action: Movement (numpy array of length 2)

        :returns: Transformed mask
        """
        potential = np.zeros_like(self.cur_obj)

        p = action_slice(potential, action)
        c = action_slice(self.cur_obj, -action)

        p[:] = c
        return potential        

    def do_safe_move(self, action):
        """
        Perform transformation specified by action if it is
        safe (does not collide with other cells and in bounds)

        :param action: Movement (numpy array of length 2)
        """
        potential = self.propose_move(action)
        
        if not grid_intersection(potential, self.grid):
            # action is safe
            self.cur_obj = potential
            self.corner[0] += action[0]
            self.corner[1] += action[1]

    def do_safe_rotate(self):
        """
        Perform rotation if it is safe (does not collide with other
        cells and in bounds)
        """
        potential = np.zeros_like(self.cur_obj)
        variations = BLOCKS[self.falling_type]
        next_type = variations[(self.version + 1) % len(variations)]

        height = len(next_type)
        width = len(next_type[0])

        x = self.corner[0]
        y = self.corner[1]

        # replace current block with rotated view
        potential[x:x+height, y:y+width] = next_type
        
        if not grid_intersection(potential, self.grid):
            # do not update corners; instead update version
            self.cur_obj = potential
            self.version = (self.version + 1) % len(variations)
        
    def gravity_step(self):
        """
        Performs a single gravity update, moving the current block down
        by one cell.

        :returns: True if the block fully landed and False otherwise
        """
        next_potential = self.propose_move(np.array([1, 0]))
        if grid_intersection(next_potential, self.grid) or np.any(self.cur_obj[-1]):
            return True
        
        self.cur_obj = next_potential
        self.corner[0] += 1
        return False

    def render(self):
        """ Renders current state onto the display """
        self.display = (self.grid + self.cur_obj)[4:, PAD:-PAD]

    def spawn_piece(self):
        """
        Spawn a new block in random location above the grid.
        """

        # randomize piece
        self.falling_type = np.random.randint(0, high=len(BLOCKS))
        to_add = BLOCKS[self.falling_type][0]
        width = len(to_add[0])
        height = len(to_add)

        # randomize column location
        spawn_point = np.random.randint(0, high=9-width)+PAD

        # replace mask with new object
        self.cur_obj.fill(0)
        self.cur_obj[:height, spawn_point:spawn_point+width] = np.array(to_add)

        # reinitialize the rotation version and corner location
        self.version = 0
        self.corner[0] = 0
        self.corner[1] = spawn_point

    def check_lines(self):
        """
        Check if any rows are completed and deletes them
        """
        cleared_rows = np.all(self.grid, axis=1).nonzero()[0]
        for row in cleared_rows:
            self.grid[1:row+1] = self.grid[:row]
            self.grid[0,PAD:-PAD].fill(0)
            self.score += 1
        
    def step(self, input):
        """
        Simulates a single frame of the game.

        :param input: The Action to take
        :return: True if the game is done
        """

        # handle direct actions
        if input == Action.ROTATE:
            self.do_safe_rotate()
        elif input == Action.LEFT:
            self.do_safe_move(np.array([0, -1]))
        elif input == Action.RIGHT:
            self.do_safe_move(np.array([0, 1]))

        # frame-based counter for the next gravity step
        if self.gravity_count >= GRAVITY_TIME or input == Action.DOWN:
            spawn_new = self.gravity_step()

            # update grid and create a new piece if the current is done
            if spawn_new:
                self.grid += self.cur_obj
                self.check_lines()
                self.spawn_piece()
            self.gravity_count = 0
        else:
            self.gravity_count += 1

        done = False
        score = self.score
        # reset if any object landed on the topmost row
        if np.any(self.grid[:5, PAD:-PAD]):
            self.reset()
            done = True
        self.render()

        return done, score


"""
Game Loop and Keyboard Logic
"""

pressed_keys = []


async def press(key):
    """ Handle key presses """
    if key in KEYS and key not in pressed_keys:
        pressed_keys.append(KEYS[key])


async def release(key):
    """ Handle key releases """
    global pressed_keys
    if key in KEYS:
        # remove all instances of key
        pressed_keys = [x for x in pressed_keys if x != KEYS[key]]


def main():
    print("Use the following keys to move the pieces:")
    print("  W - Rotate")
    print("  A - Move left")
    print("  S - Move down")
    print("  D - Move right")
    print()
    print("You can also press Q to quit and R to restart")
    # create display on computer and Arduino
    cv_out = CV2Display()
    ard_out = ArduinoDisplay(use_audio=False)
    output = MultiDisplay([cv_out, ard_out])

    tetris = Tetris()

    done = False

    while True:
        start_time = time.time()

        if len(pressed_keys) == 0:
            action = 0
        elif action == pressed_keys[0]:
            action = 0
        else:
            action = pressed_keys[0]

        if action == Action.RESTART:
            tetris.reset()
            done = False

        if done or action == Action.QUIT:
            # print(score//10)
            done = True
            output.set_frame(display_for_num(score))
            # score += 1
        else:
            done, score = tetris.step(action)
            output.set_frame(np.where(tetris.display == 0, 0, tetris.display+8))

        # lock simulation rate to 30 Hz
        time.sleep(max(1/30 - (time.time() - start_time), 0))


if __name__ == '__main__':
    # create thread for asynchronous input
    thread = Thread(target=lambda: listen_keyboard(
        on_press=press,
        on_release=release,
        delay_second_char=0
    ), daemon=True)
    thread.start()
    main()
