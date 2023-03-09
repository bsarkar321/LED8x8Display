# LED8x8Display
Code for working with 8x8 LED matrix

## Installation

First clone the git repository using `git clone https://github.com/bsarkar321/LED8x8Display` and cd into the LED8x8Display directory.

For Arduino support, you need the Arduino IDE to upload the ino file. You also need to install the Arduino FFT Library from Open Music Labs (V3.0 or higher).

Using pip, you also need to install opencv-python, numpy, tqdm, pyserial, playsound, and sshkeyboard.

## Running the program

First, upload the `arduino_code.ino` onto your arduino mini. You may need to modify the `ANODE_PINS` and `CATHODE_PINS` depending on your setup. After uploading, you can quit the IDE; everything else happens in the terminal.

To run a python file, simply run `python [filename.py]` in this directory.

## Troubleshooting

You might experience an error like `AttributeError: 'ArduinoDisplay' object has no attribute 'serialcomm'`. This indicates one of two things: (1) the USB port is currently busy, so you should quit the Arduino IDE, or (2) you haven't plugged the arduino into the correct port. By default, your computer will look for the arduino at `/dev/cu.usbserial-3`, but you might need to change that depending on your system. This can be changed in `display.py` where the default parameters for the ArduinoDisplay port reside. Make sure you change it to the port you used for uploading to the arduino.


## Using, Modifying, and Distributing

This repository is free and open source, distributed under GNU GPL-v3, a strong copy-left license. Please read the LICENSE file for more information.
