"""
Script to compress frames of Bad Apple into an npy file for
8x8 rendering.

First you must create the frames folder (within the bad_apple_utils folder):

mkdir frames
ffmpeg -i badapple.mp4 frames/badapple_%04d.png
"""

import os
import numpy as np
import cv2
import time
from tqdm import tqdm

compressed_vid = np.zeros((len(os.listdir('frames')), 8, 8))

for i, file in enumerate(tqdm(sorted(os.listdir('frames')))):
    img = cv2.imread('frames/' + file)
    res = cv2.resize(img, dsize=(8, 8), interpolation=cv2.INTER_AREA)
    compressed_vid[i] = res[:, :, 0] / 255

np.save('badapple_compressed.npy', compressed_vid)
