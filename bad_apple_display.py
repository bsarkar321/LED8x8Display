"""
Play the music video for 'Bad Apple' on the 8x8 display.
"""

import serial
import time
import numpy as np
from tqdm import tqdm

import cv2

from display import CV2Display, ArduinoDisplay, MultiDisplay
from threading import Thread

from playsound import playsound

cv_out = CV2Display()
ard_out = ArduinoDisplay(use_audio=False)

output = MultiDisplay([cv_out, ard_out])

compressed_vid = np.load('bad_apple_utils/badapple_compressed.npy')

# thread = Thread(target=lambda: , daemon=True)
playsound('bad_apple_utils/badapple.mp4', block=False)
# thread.start()

frames = (compressed_vid * 15)
frames = frames.astype('byte')

print(len(frames))


start_time = time.time()

for i, frame in enumerate(tqdm(frames)):
    output.set_frame(frame)
    time.sleep(max(i/30 - (time.time() - start_time), 0))

# thread.join()
