pip3 install pyinstaller
rmdir /S /Q build
rmdir /S /Q dist
pyinstaller --noconfirm --onefile --windowed --icon "Disease Sim Icon.ico" --name "Disease Simulator"  "src\bundled.py"