#!/bin/bash

VERSION=1.16.5
URL=https://github.com/hrydgard/ppsspp.git

for u in $URL; do
  mkdir -p ppsspp && pushd ppsspp
  git clone -b v$VERSION --depth 1 --single-branch --progress --recursive $URL
  cd ppsspp/ffmpeg
  rm -rf ios Windows* windows* macosx blackberry* gas-preprocessor symbian* wiiu
  cd ..
  rm -rf ios Windows* windows* macosx blackberry* symbian*
  rm -rf dx9sdk pspautotests MoltenVK
  cd ..
#  find ppsspp -type d \( -name "ffmpeg" \) -exec rm -rf {} ';'
  find ppsspp/android -perm /644 -type f \( -name "*.a" \) -exec rm -f {} ';'
  find ppsspp -type d \( -name ".git*" \) -exec rm -rf {} ';'
  find ppsspp -type f \( -name ".gitignore" \) -exec rm -rf {} ';'
  find ppsspp -type f \( -name "*.a" \) -exec rm -rf {} ';'
  popd
  tar -czvf ppsspp-ffmpeg-$VERSION.tar.gz ppsspp
  rm -rf ppsspp
done
exit 0
