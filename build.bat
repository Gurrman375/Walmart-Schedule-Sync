set PLAYWRIGHT_BROWSERS_PATH=0
playwright install chromium
pyinstaller -F --noconfirm --onedir --console --icon ".\BCO.ab709918-e5d9-4202-a572-086577a921ab.ico"  ".\wss.py"