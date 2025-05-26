#!/bin/bash
apt-get update && apt-get install -y ffmpeg
mkdir -p downloads
python3 BOT.py
