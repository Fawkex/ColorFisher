#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# encoding: utf-8
#
#  ColorFisher
#
# Copyright 2021 FawkesPan
# Contact : i@fawkex.me / Telegram@FawkesPan
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
#                    Version 2, December 2004 
#
# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net> 
#
# Everyone is permitted to copy and distribute verbatim or modified 
# copies of this license document, and changing it is allowed as long 
# as the name is changed. 
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION 
#
#  0. You just DO WHAT THE FUCK YOU WANT TO.
#

import sys
import time
import mouse
import logging
import keyboard
import pyautogui
import threading
from PIL import Image
import numpy as np

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

working = False
hooked_threshold = 5
allowed_color_shift = [5, 5, 5]

def wait():
    while True:
        try:
            time.sleep(86400)
        except KeyboardInterrupt:
            get_to_rest()
            logging.info('Exited.')
            tf.reset_default_graph()
            sys.exit(0)

crop_percent = 0.25
target_size = 128, 128
def take_screenshot():
    sc = pyautogui.screenshot()
    width, height = sc.size
    crop_size = int(min(width, height)*crop_percent)
    left = (width - crop_size)/2
    top = (height - crop_size)/2
    right = (width + crop_size)/2
    bottom = (height + crop_size)/2
    cropped = sc.crop((left, top, right, bottom))
    resized = cropped.resize(target_size, resample=Image.NEAREST)
    return resized

LIGHT_RED = [211, 42, 42]
DARK_RED = [137, 20, 20]
def count_color(img, color):
    count = sum(abs(img.reshape(-1, 3) - color) < allowed_color_shift).min()
    return count

def get_current_color_counts():
    img = take_screenshot()
    img_arr = np.array(img)
    dark_red_count = count_color(img_arr, DARK_RED)
    light_red_count = count_color(img_arr, LIGHT_RED)
    return [dark_red_count, light_red_count]

def fisherman_thread():
    global working
    last_click = time.time()
    history = []
    while True:
        if working:
            try:
                color_counts = get_current_color_counts()
            except:
                continue
            status = True if sum(color_counts) < hooked_threshold else False
            logging.info('Dark red: %d Light red: %d Rod Status: %s.'% (color_counts[0], color_counts[1], 'Idling' if status else 'Luring'))
            history.append(status)
            if len(history) > 100:
                history = history[-100:]
            if len(history) > 10:
                if time.time() - last_click < 2:
                    continue
                if all(history[-10:]):
                    logging.info('We are not fishing yet.')
                    logging.info('Throwing.')
                    mouse.right_click()
                    last_click = time.time()
                elif all(history[-1:]):
                    logging.info('We have fish hooked. Retracting.')
                    mouse.right_click()
                    time.sleep(0.8)
                    logging.info('Throwing.')
                    mouse.right_click()
                    last_click = time.time()
                else:
                    pass
        else:
            history = []
            time.sleep(0.01)

def get_to_work():
    global working
    working = True
    logging.info('Fisherman started working.')

def get_to_rest():
    global working
    working = False
    logging.info('Fisherman will take some rest.')
    

threading.Thread(target=fisherman_thread, daemon=True).start()

def main():
    keyboard.add_hotkey('f7', get_to_work, args=(), suppress=False,
            timeout=1, trigger_on_release=False)
    keyboard.add_hotkey('f8', get_to_rest, args=(), suppress=False,
            timeout=1, trigger_on_release=False)
    logging.info('F7: Begin fishing, F8: End fishing.')
    wait()

if __name__ == '__main__':
    main()
