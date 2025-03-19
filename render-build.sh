#!/usr/bin/env bash

# Устанавливаем Google Chrome
wget -qO- https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb > chrome.deb
apt-get update && apt-get install -y ./chrome.deb
rm chrome.deb

# Устанавливаем ChromeDriver
CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)
wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
rm chromedriver_linux64.zip
chmod +x chromedriver
mv chromedriver /usr/local/bin/
