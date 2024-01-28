#!/bin/sh
# Create a folder (named dmg) to prepare our DMG in (if it doesn't already exist).
mkdir -p dist/dmg
# Empty the dmg folder.
rm -r dist/dmg/*
# Copy the app bundle to the dmg folder.
cp -r "dist/AI_Bottom.app" dist/dmg
# If the DMG already exists, delete it.
test -f "dist/AI_Bottom.dmg" && rm "dist/AI_Bottom.dmg"
create-dmg \
  --volname "AI_Bottom" \
  --volicon "asset/ai.icns" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "AI_Bottom.app" 175 120 \
  --hide-extension "AI_Bottom.app" \
  --app-drop-link 425 120 \
  "dist/AI_Bottom.dmg" \
  "dist/dmg/"