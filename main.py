import ctypes
import json
import logging
import os
import sys
import time
from dataclasses import dataclass

import pystray
import requests
from PIL import Image

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        # If running in a PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)  # noqa
    return os.path.join(os.path.abspath("."), relative_path)


REQUEST_TIMEOUT = 5
PIRATE_FLAG = resource_path("assets/images/pirate_flag.png")

with open(resource_path("assets/cc_to_country.json")) as f:
    CC_TO_COUNTRY = json.load(f)


@dataclass
class IPData:
    ip: str
    country_code: str | None
    country: str
    city: str


def ip_prefer_method() -> IPData:
    url = "http://ip-api.com/json/?fields=country,countryCode,city,query"
    r = requests.get(url, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    ip_data = IPData(ip=data.get("query", "Unknown IP"),
                     country_code=data.get("countryCode"),
                     country=data.get("country", "Unknown country"),
                     city=data.get("city", "Unknown city"))
    return ip_data


def ip_fallback_method() -> IPData:
    url = "https://ipinfo.io/json"
    r = requests.get(url, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    ip_data = IPData(ip=data.get("ip", "Unknown IP"),
                     country_code=data.get("country"),
                     country=CC_TO_COUNTRY.get(data["country"], "Unknown country"),
                     city=data.get("city", "Unknown city"))
    return ip_data


def find_ip() -> None | IPData:
    try:
        try:
            try:
                return ip_prefer_method()
            except requests.RequestException:
                return ip_fallback_method()
        except requests.RequestException:
            return None
    except Exception as e:
        logger.exception(e)
        # Show error text instead of ip info
        ip_error_data = IPData(ip=str(e),
                               country_code=None,
                               country="APP ERROR",
                               city="")
        return ip_error_data


class Application:
    def __init__(self):
        self.stop_program = False
        self.last_ip = None
        self.tray = pystray.Icon("My IP in System Tray")
        self.tray.icon = Image.open(PIRATE_FLAG)
        self.tray.menu = pystray.Menu(pystray.MenuItem("Quit", lambda: self.quit_window()))
        self.tray.run_detached()

    def quit_window(self):
        logger.info("Quit by user right click")
        self.stop_program = True
        self.tray.stop()
        os._exit(0)  # noqa

    def __update_tray(self, ip_data: IPData):
        if ip_data.country_code and ip_data.country_code in CC_TO_COUNTRY:
            icon_path = resource_path(f"assets/images/flags/{ip_data.country_code}.png")
            self.tray.icon = Image.open(icon_path)
        else:
            icon_path = resource_path("assets/images/unknown_cc.png")
            self.tray.icon = Image.open(icon_path)

        self.tray.title = f"{ip_data.country}\n{ip_data.city}\n{ip_data.ip}"

    def update_data(self):
        while not self.stop_program:
            ip_data = find_ip()
            if ip_data:
                if ip_data.ip != self.last_ip:
                    self.last_ip = ip_data.ip
                    self.__update_tray(ip_data)
            else:
                self.last_ip = None
                self.tray.icon = Image.open(PIRATE_FLAG)
                self.tray.title = "No Internet"
            time.sleep(5)

    def run(self):
        if sys.platform in ["win32", "win64", "cygwin", "msys"]:
            try:
                # if your Windows version >= 8.1
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except:  # noqa
                # win 8.0 or less
                ctypes.windll.user32.SetProcessDPIAware()

        self.update_data()
        os._exit(42)  # noqa


if __name__ == "__main__":
    pid_msg = f"My IP in system tray PID: {os.getpid()}"
    logger.info(pid_msg)
    app = Application()
    app.run()
