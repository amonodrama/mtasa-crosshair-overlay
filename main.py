import tkinter as tk
import win32gui
import win32con
import win32api
import configparser
import keyboard
import threading
import time

def make_window_click_through(hwnd):
    print(f"CIT Crosshair Overlay by monodrama Started")
    styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)

def load_config():
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_option("Crosshair", "color"):
        config.set("Crosshair", "color", "255,0,0")
    if not config.has_option("Crosshair", "style"):
        config.set("Crosshair", "style", "lines")
    if not config.has_option("Crosshair", "size"):
        config.set("Crosshair", "size", "15")
    if not config.has_option("Crosshair", "line_width"):
        config.set("Crosshair", "line_width", "2")
    return config

def update_crosshair_position():
    global current_offset_x, current_offset_y, last_offset_x, last_offset_y, current_color
    for section in config.sections():
        if section != "Crosshair":
            keys = config.get(section, "keys").split(",")
            for key in keys:
                key = key.strip()
                if keyboard.is_pressed(key):
                    new_offset_x = int(config.get(section, "offset_x"))
                    new_offset_y = int(config.get(section, "offset_y"))
                    if new_offset_x != last_offset_x or new_offset_y != last_offset_y:
                        current_offset_x = new_offset_x
                        current_offset_y = new_offset_y
                        print(f"Weapon: {section}, Offset X: {current_offset_x}, Offset Y: {current_offset_y}")
                        move_crosshair()
                        last_offset_x, last_offset_y = current_offset_x, current_offset_y
                    return

def move_crosshair():
    center_x = (screen_width // 2) + current_offset_x
    center_y = (screen_height // 2) + current_offset_y
    canvas.delete("all")
    if crosshair_style == "circle":
        radius = crosshair_size
        canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius,
                           outline=f"#{current_color[0]:02x}{current_color[1]:02x}{current_color[2]:02x}",
                           width=line_width)
    else:
        canvas.create_line(center_x - crosshair_size, center_y, center_x + crosshair_size, center_y,
                           fill=f"#{current_color[0]:02x}{current_color[1]:02x}{current_color[2]:02x}",
                           width=line_width)
        canvas.create_line(center_x, center_y - crosshair_size, center_x, center_y + crosshair_size,
                           fill=f"#{current_color[0]:02x}{current_color[1]:02x}{current_color[2]:02x}",
                           width=line_width)
    print(f"Crosshair moved to ({center_x}, {center_y}), Color: {current_color}, Style: {crosshair_style}") #debug

root = tk.Tk()
root.title("cit crosshair overlay")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}+0+0")
root.overrideredirect(True)
root.attributes("-topmost", True)
root.update_idletasks()

windowname = win32gui.FindWindow(None, "cit crosshair overlay")
if windowname:
    make_window_click_through(windowname)

canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg="black", highlightthickness=0)
canvas.pack()

config = load_config()

current_offset_x = 0
current_offset_y = 0
last_offset_x = 0
last_offset_y = 0

color_str = config.get("Crosshair", "color")
current_color = tuple(map(int, color_str.split(",")))
crosshair_style = config.get("Crosshair", "style")
crosshair_size = int(config.get("Crosshair", "size"))
line_width = int(config.get("Crosshair", "line_width"))

def check_keys():
    while True:
        update_crosshair_position()
        time.sleep(0.01) #ingame delay fix

def key_polling_thread():
    while True:
        update_crosshair_position()
        time.sleep(0.01) #ingame delay fix do not remove

thread = threading.Thread(target=key_polling_thread, daemon=True)
thread.start()

move_crosshair()

root.mainloop()
