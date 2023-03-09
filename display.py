"""
Definitions of various outpus for 8x8 display.
"""

from threading import Lock, Thread
from time import sleep

import cv2
import serial

import numpy as np

class Display8x8():
    """
    Generic 8x8 display interface.

    Each frame is an 8x8 numpy array of bytes with values
    from 0 to 15 (inclusive), where 0 is off and 15 is the
    brightest.
    """

    def __init__(self):
        self.cur_frame = np.zeros((8, 8), dtype=np.byte)

    def set_frame(self, new_frame):
        self.cur_frame = new_frame
        self._display_fn(self.cur_frame)

    def _display_fn(self, frame):
        pass


class AsyncDisplay(Display8x8):
    """
    Asynchronous display using python threading.

    It updates at a fixed interval instead of updating whenever
    set_frame is called.
    """
    def __init__(self, fps=30):
        super().__init__()
        self.frame_lock = Lock()
        self.fps = fps
        self.running = True
        self.thread = Thread(target=self._display, daemon=True)
        self.thread.start()

    def __del__(self):
        # Need to close thread in destructor
        self.running = False
        self.thread.join()

    def set_frame(self, new_frame):
        self.frame_lock.acquire()
        self.cur_frame = new_frame
        self.frame_lock.release()

    def _display(self):
        while self.running:
            self.frame_lock.acquire()
            self._display_fn(self.cur_frame)
            self.frame_lock.release()
            sleep(1/self.fps)

            
class CV2Display(Display8x8):
    """
    Virtual display on computer screen using opencv
    """

    def __init__(self):
        cv2.startWindowThread()
        cv2.namedWindow('Preview')
        super().__init__()

    def _display_fn(self, frame):
        # convert to [0,1] instead of [0, 15]
        res = frame.astype('float')/15
        rescale = cv2.resize(res, dsize=(480, 480), interpolation=cv2.INTER_NEAREST)
        cv2.imshow('Preview', rescale)
        cv2.waitKey(1)

class ArduinoDisplay(AsyncDisplay):
    """
    Interface for Arduino 8x8 LED display.
    """

    def __init__(self, port='/dev/cu.usbserial-3', baud_rate=115200, fps=30, use_audio=True):
        self.serialcomm = serial.Serial(port, baud_rate)
        self.use_audio = use_audio
        print("Serial communication running on Port " + port + " at a baud rate of", baud_rate)
        super().__init__(fps=fps)

    def __del__(self):
        self.serialcomm.close()
        super().__del__()

    def _display_fn(self, frame):
        # compress frame into 32 bytes to prevent flickering
        f = frame.flatten()
        compressed_frame = f[::2] + (f[1::2] * (2 ** 4))
        compressed_frame = np.append(compressed_frame, [self.use_audio])
        self.serialcomm.write(compressed_frame.tobytes())


class MultiDisplay(Display8x8):
    """
    Display that is a combination of other displays.

    This can be used to have an active Arduino and CV2 display
    """
    def __init__(self, displays):
        self.displays = displays
        super().__init__()

    def set_frame(self, new_frame):
        super().set_frame(new_frame)
        for display in self.displays:
            display.set_frame(new_frame)
