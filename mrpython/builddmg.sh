#! /bin/sh

# from: https://www.pythonguis.com/tutorials/packaging-pyqt5-applications-pyinstaller-macos-dmg/

# Create a folder (named dmg) to prepare our DMG in (if it doesn't already exist).
mkdir -p dist/dmg
# Empty the dmg folder.
rm -r dist/dmg/*
# Copy the app bundle to the dmg folder.
cp -r "dist/MrPython.app" dist/dmg
# If the DMG already exists, delete it.
test -f "dist/MrPython.dmg" && rm "dist/MrPython.dmg"
create-dmg \
  --volname "MrPython" \
  --window-pos 100 100 \
  --window-size 1024 768 \
  --icon-size 100 \
  --icon "MrPython.app" 175 120 \
  --hide-extension "MrPython.app" \
  --app-drop-link 425 120 \
  "dist/MrPython.dmg" \
  "dist/dmg/"
