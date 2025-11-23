import ctypes
import json
import logging
import os
import sys
import threading
import time
import tkinter

import pystray
import requests
from PIL import Image


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        # If running in a PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path) # noqa
    return os.path.join(os.path.abspath("."), relative_path)


REQUEST_TIMEOUT = 5
PIRATE_FLAG = resource_path("assets/images/pirate_flag.png")

with open(resource_path("assets/cc_to_country.json")) as f:
    CC_TO_COUNTRY = json.load(f)


def ip_prefer_method() -> dict:
    """Return must include keys: ip, countryCode, country, city"""
    url = "http://ip-api.com/json/?fields=country,countryCode,city,query"
    r = requests.get(url, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    data["ip"] = data["query"]
    return data


def ip_second_method() -> dict:
    """Return must include keys: ip, countryCode, country, city"""
    url = "https://ipinfo.io/json"
    r = requests.get(url, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    data["countryCode"] = data["country"]
    data["country"] = CC_TO_COUNTRY[data["countryCode"]]
    return data


def find_ip() -> None | dict:
    try:
        try:
            try:
                return ip_prefer_method()
            except requests.RequestException:
                return ip_second_method()
        except requests.RequestException:
            return None
    except Exception as e:
        logging.exception(e)


class Application:
    def __init__(self):
        self.stop_program = False
        self.last_ip = None

        self.root = tkinter.Tk()

        self.icon = pystray.Icon("My IP in System Tray")
        self.icon.icon = Image.open(PIRATE_FLAG)
        self.icon.menu = pystray.Menu(pystray.MenuItem("Quit", lambda: self.quit_window()))
        self.icon.run_detached()

        self.thread2 = threading.Thread(target=self.update_data)
        self.thread2.start()
        self.root.withdraw()

    def quit_window(self):
        print("Quit by user click")
        self.stop_program = True
        self.icon.icon = None
        self.icon.title = None
        self.icon.stop()
        self.root.destroy()

    def __update_tray(self, ip_data: dict):
        ip_address = ip_data["ip"]
        country = ip_data.get("country", "Unknown country")
        city = ip_data.get("city", "Unknown city")

        cc = ip_data.get('countryCode', None)
        if cc and cc in CC_TO_COUNTRY:
            icon_path = resource_path(f"assets/images/flags/{cc}.png")
            self.icon.icon = Image.open(icon_path)

        self.icon.title = f"{country}\n{city}\n{ip_address}"

    def update_data(self):
        while not self.stop_program:
            ip_data = find_ip()
            if ip_data:
                if ip_data["ip"] != self.last_ip:
                    self.last_ip = ip_data["ip"]
                    self.__update_tray(ip_data)
            else:
                self.last_ip = None
                self.icon.icon = Image.open(PIRATE_FLAG)
                self.icon.title = "No Internet"
            time.sleep(5)

    def run(self):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # if your Windows version >= 8.1
        except: # noqa
            ctypes.windll.user32.SetProcessDPIAware()  # win 8.0 or less

        self.root.mainloop()
        os._exit(42) # noqa


if __name__ == "__main__":
    app = Application()
    app.run()
