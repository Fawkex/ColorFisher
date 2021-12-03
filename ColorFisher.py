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

import os
import sys
import time
import logging
import keyboard
import pyautogui
import threading
from PIL import Image
import numpy as np

INFO_LEVEL = logging.INFO
__version__ = "1.4.1"
MAX_FPS = 5

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=INFO_LEVEL)

working = False
hooked_threshold = 0

def wait():
    while True:
        try:
            time.sleep(86400)
        except KeyboardInterrupt:
            get_to_rest()
            logging.info('Exited.')
            sys.exit(0)

# 截图函数
crop_percent = 0.4
target_size = 256, 256
def default_take_screenshot():
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

def d3d_take_screenshot():
    width, height = d.display.resolution
    crop_size = int(min(width, height)*crop_percent)
    left = int((width - crop_size)/2)
    top = int((height - crop_size)/2)
    right = int((width + crop_size)/2)
    bottom = int((height + crop_size)/2)
    sc = d.screenshot(region=(left, top, right, bottom))
    resized = sc.resize(target_size, resample=Image.NEAREST)
    return resized

# Windows下用DX效率更高
if os.name == 'nt':
    import d3dshot
    d = d3dshot.create(capture_output="pil")
    take_screenshot = d3d_take_screenshot
    logging.debug('DirectX API Enabled.')
else:
    take_screenshot = default_take_screenshot

DARK_RED = [[137, 20, 20], [10, 5, 5]]
LIGHT_RED = [[211, 42, 42], [10, 5, 5]]
ROD_WHITE = [[208, 208, 208], [10, 10, 12]]
ROD_GREY = [[143, 143, 143], [5, 5, 5]]
def count_color(img, color):
    reshaped = img.reshape(-1, 3)
    start = time.time()
    diffs = np.subtract(reshaped, color[0])
    abs_diffs = np.absolute(diffs)
    count = np.sum(abs_diffs <= color[1], axis=0).min()
    logging.debug('Count Time: %.4f' % (time.time()-start))
    return count

def get_current_color_counts():
    img = take_screenshot()
    img_arr = np.array(img)
    #dark_red_count = count_color(img_arr, DARK_RED)
    dark_red_count = 65535
    light_red_count = count_color(img_arr, LIGHT_RED)
    rod_white_count = count_color(img_arr, ROD_WHITE)
    #rod_grey_count = count_color(img_arr, ROD_GREY)
    rod_grey_count = 65535
    return [dark_red_count, light_red_count, rod_white_count, rod_grey_count]

def fisherman_thread():
    global working
    last_click = time.time()
    history = []
    frametime_history = []
    fps_control_delay = 0.12
    while True:
        if working:
            begin_time = time.time()
            time.sleep(fps_control_delay)
            try:
                color_counts = get_current_color_counts()
                frametime_history.append(time.time()-begin_time)
                average_frametime = np.average(frametime_history[-50:])
                average_fps = 1/average_frametime
                logging.debug('Average FPS: %.3f' % average_fps)
                logging.debug('Average Frametime: %.3f ms' % (average_frametime*1000))
                logging.debug('FPS Control Delay: %.3f ms' % (fps_control_delay*1000))
                if average_fps > MAX_FPS:
                    fps_control_delay += 0.0002
                else:
                    fps_control_delay = max(0, fps_control_delay-0.0002)
            except:
                continue
            status = False
            if color_counts[1] <= hooked_threshold:
                status = True
            if color_counts[1]+color_counts[2] <= 5:
                status = True
            logging.info('红色像素数量: %d 白色像素数量: %d 鱼竿状态: %s.'% (color_counts[1], color_counts[2], '闲置中' if status else '钓鱼中'))
            history.append(status)
            if len(history) > 100:
                history = history[-100:]
            if len(history) > 10:
                if time.time() - last_click < 2:
                    continue
                if all(history[-10:]):
                    logging.info('还没在钓鱼.')
                    logging.info('丢杆.')
                    pyautogui.click(button='right')
                    last_click = time.time()
                elif all(history[-1:]):
                    logging.info('有鱼上钩了. 收杆.')
                    pyautogui.click(button='right')
                    time.sleep(0.8)
                    logging.info('丢杆.')
                    pyautogui.click(button='right')
                    last_click = time.time()
                else:
                    pass
        else:
            history = []
            frametime_history = frametime_history[-100:]
            time.sleep(0.01)

def get_to_work():
    global working
    working = True
    logging.info('钓鱼佬开始工作.')

def get_to_rest():
    global working
    working = False
    logging.info('钓鱼佬要休息了.')
    

threading.Thread(target=fisherman_thread, daemon=True).start()

def main():
    keyboard.add_hotkey('f7', get_to_work, args=(), suppress=False,
            timeout=1, trigger_on_release=False)
    keyboard.add_hotkey('f8', get_to_rest, args=(), suppress=False,
            timeout=1, trigger_on_release=False)
    logging.info('----------- ColorFisher -----------')
    logging.info('Version: v%s' % __version__)
    logging.info('F7: 开始钓鱼, F8: 停止钓鱼.')
    logging.info('使用建议:')
    logging.info('    ① 把游戏亮度调到最高.')
    logging.info('    ② 游戏窗口最大化, 不需要全屏. 如果屏幕比例不是16:9, 可以把游戏窗口拉到16:9左右.')
    logging.info('    ③ 钓鱼的地方需要有良好照明，否则夜间无法正常使用.')
    logging.info('      在水面上留空两格，第三格插火把即可, 但不要挡住吊钩正上方天空.')
    logging.info('      如果将游戏 gamma 参数设为 500 , 则可以不考虑照明问题.')
    logging.info('    ④ 使用原版材质包, 程序根据原版材质包中浮标的颜色编写, 非原版可能无法正常使用.')
    logging.info('    ⑤ 游戏最高帧数可以限制至 10 FPS，将显著降低显卡功耗.')
    logging.info('    ⑥ （可选）将游戏场视角调至最低, 且保证抛竿角度可以使得每次抛竿后浮标都在准星附近.')
    logging.info('      可极大提高识别准确率.')
    wait()

if __name__ == '__main__':
    main()
