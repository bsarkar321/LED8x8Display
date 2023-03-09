"""
Set arduino to show frequency of music
"""

import time

from display import CV2Display, ArduinoDisplay, MultiDisplay

import numpy as np

def main():
    # create display on computer and Arduino
    cv_out = CV2Display()
    ard_out = ArduinoDisplay(use_audio=True)
    output = MultiDisplay([cv_out, ard_out])

    output.set_frame(np.ones((8, 8), dtype=np.byte) * 15)
    time.sleep(1)


if __name__ == '__main__':
    main()
