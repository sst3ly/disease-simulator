pip install py2app
rm -rf setup.py
rm -rf build
rm -rf dist
py2applet --make-setup src/bundled.py
py2applet setup.py py2app -A