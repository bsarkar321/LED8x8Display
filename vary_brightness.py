"""
Simple script for changing brightness from 0 to 15 and back to 0 in loop.
"""

import time

from display import CV2Display, ArduinoDisplay, MultiDisplay
import numpy as np

def main():
    # create display on computer and Arduino
    cv_out = CV2Display()
    ard_out = ArduinoDisplay(use_audio=False)
    output = MultiDisplay([cv_out, ard_out])

    iteration = 0

    while True:
        start_time = time.time()
        output.set_frame(np.ones((8, 8), dtype=np.byte) * (15 - abs(15-iteration)))
        iteration = (iteration + 1) % 30
        # lock simulation rate to 1 Hz
        time.sleep(max(1 - (time.time() - start_time), 0))


if __name__ == '__main__':
    main()
