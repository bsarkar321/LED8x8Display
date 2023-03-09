"""
Simple timer using python to test displaying numbers
"""

import time

from display import CV2Display, ArduinoDisplay, MultiDisplay

from utils import display_for_num

def main():
    # create display on computer and Arduino
    cv_out = CV2Display()
    ard_out = ArduinoDisplay(use_audio=False)
    output = MultiDisplay([cv_out, ard_out])

    iteration = 0

    while True:
        start_time = time.time()
        output.set_frame(display_for_num(iteration))
        iteration += 1
        # lock simulation rate to 1 Hz
        time.sleep(max(1 - (time.time() - start_time), 0))


if __name__ == '__main__':
    main()
