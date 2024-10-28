pip install py2app
rm -rf setup.py
rm -rf build
rm -rf dist
py2applet --make-setup src/bundled.py "Disease Sim Icon.icns"
match='setup('
insert='    name="Disease Simulator",'
sed -i "" "s/$match/$match\n$insert/" setup.py
python setup.py py2app -A