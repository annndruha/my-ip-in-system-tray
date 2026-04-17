# My IP in system tray

Show IP information in system tray. Used two geo-ip providers: `ip-api.com` and `ipinfo.io` as fallback. Updated every 5 seconds.

## How it works
* Flag in tray 
* IP Info on mouse hover
* Quit by right click menu

![On hover](docs/on_hover.png)

#### [Windows] Executable 

* **Download pre-builded .exe**
  * Download exe-file form [releases](https://github.com/annndruha/my-ip-in-system-tray/releases)

* or **build .exe yourself**
  * Run `pip install pyinstaller`
  * Build `.exe` yourself by run `build.bat`

* **Add it to "Startup apps"**
  * Copy `.exe` file to startup directory:
  ```
  C:\Users\%USERNAME%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
  ```

#### [Other OS] Run python

```bash
pip install -r requirements.txt
python main.py
```
