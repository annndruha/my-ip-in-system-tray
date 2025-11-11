import ctypes
import json
import os
import sys
import threading
import time
import tkinter

import pystray
import requests
from PIL import Image
from pystray import Menu, MenuItem


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        # If running in a PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


REQUEST_TIMEOUT = 5
IMG_DIR = resource_path("assets/images")
PIRATE_FLAG = f"{IMG_DIR}/pirate_flag.png"

with open(f"{resource_path('assets')}/cc_to_country.json") as f:
    CC_TO_COUNTRY = json.load(f)


def ip_prefer_method() -> dict:
    """Return must include keys: ip, countryCode, country, city"""
    r = requests.get("https://ipinfo.io/json", timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    data['countryCode'] = data["country"]
    data['country'] = CC_TO_COUNTRY[data['countryCode']]
    return data


def ip_fallback_method() -> dict:
    """Return must include keys: ip, countryCode, country, city"""
    r = requests.get("http://ip-api.com/json/", timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    data["ip"] = data["query"]
    return data


def find_ip() -> None | dict:
    try:
        try:
            return ip_prefer_method()
        except requests.RequestException:
            return ip_fallback_method()
    except Exception as e:
        print(e)


class Application:
    def __init__(self):
        self.stop_program = False
        self.last_ip = None

        self.root = tkinter.Tk()

        self.icon = pystray.Icon("My IP in System Tray")
        self.icon.icon = Image.open(PIRATE_FLAG)
        self.icon.menu = Menu(MenuItem('Quit', lambda: self.quit_window()))
        self.icon.run_detached()

        self.thread2 = threading.Thread(target=self.update_data)
        self.thread2.start()
        self.root.withdraw()

    def quit_window(self):
        print('Quit by user click')
        self.stop_program = True
        self.icon.icon = None
        self.icon.title = None
        self.icon.stop()
        self.root.destroy()

    def update_data(self):
        while not self.stop_program:
            ip = find_ip()
            if ip:
                ip_address = ip["ip"]
                if ip_address != self.last_ip:
                    self.last_ip = ip_address
                    self.icon.icon = Image.open(f"{IMG_DIR}\\flags\\{ip['countryCode']}.png")
                    self.icon.title = ip['country'] + '\n' + ip['city'] + '\n' + ip_address
            else:
                self.last_ip = None
                self.icon.icon = Image.open(PIRATE_FLAG)
                self.icon.title = "No Internet"
            time.sleep(5)

    def run(self):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # if your Windows version >= 8.1
        except:
            ctypes.windll.user32.SetProcessDPIAware()  # win 8.0 or less

        self.root.mainloop()
        os._exit(42)


if __name__ == '__main__':
    app = Application()
    app.run()
