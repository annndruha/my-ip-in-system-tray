pyinstaller --clean ^
  --noconsole ^
  --name "My_IP_in_system_tray"  ^
  --onefile main.py ^
  --add-data=assets/;assets/ ^
  --icon assets/images/icon.ico ^
  --distpath . ^
  --version-file=version.txt
  --hidden-import json ^
  --hidden-import ctypes ^
  --hidden-import pystray ^
  --hidden-import platform ^
  --hidden-import PIL ^
  --hidden-import PIL.Image

IF EXIST build (rmdir /q /s build)
DEL My_IP_in_system_tray.spec