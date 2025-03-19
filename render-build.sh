#!/usr/bin/env bash

# Создаём директорию для Chrome и ChromeDriver
mkdir -p ~/chrome && cd ~/chrome

# Скачиваем и распаковываем Chrome
wget -qO- https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb > chrome.deb
dpkg-deb -x chrome.deb .
rm chrome.deb

# Скачиваем и распаковываем ChromeDriver
CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE)
wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
rm chromedriver_linux64.zip
chmod +x chromedriver

echo "Chrome и ChromeDriver установлены в ~/chrome"
