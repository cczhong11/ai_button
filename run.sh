#!/bin/sh
# Create a folder (named dmg) to prepare our DMG in (if it doesn't already exist).
mkdir -p dist/dmg
# Empty the dmg folder.
rm -r dist/dmg/*
# Copy the app bundle to the dmg folder.
cp -r "dist/AI_Button.app" dist/dmg
# If the DMG already exists, delete it.
test -f "dist/AI_Button.dmg" && rm "dist/AI_Button.dmg"
create-dmg \
  --volname "AI_Button" \
  --volicon "asset/ai.icns" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "AI_Button.app" 175 120 \
  --hide-extension "AI_Button.app" \
  --app-drop-link 425 120 \
  "dist/AI_Button.dmg" \
  "dist/dmg/"