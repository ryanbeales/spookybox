#!/bin/bash

# Install GPIO packages
apt-get install pigpio python3-pigpio

# Install python libraries
pip3 install -r /home/pi/src/spookybox/requirements.txt

# Download and make mjpg-streamer for raspberry pi
apt-get install cmake libjpeg8-dev gcc
curl -fsSLO --compressed --retry 3 --retry-delay 10 https://github.com/jacksonliam/mjpg-streamer/archive/master.tar.gz && mkdir /mjpg && tar xzf master.tar.gz -C /mjpg
cd  /mjpg/mjpg-streamer-master/mjpg-streamer-experimental
make 
make install

cp /home/pi/src/spookybox/services/*.service /etc/systemd/system

# Start services
systemctl daemon-reload
systemctl enable pigpiod; systemctl start pigpiod
systemctl enable mjpg-streamer; systemctl start mjpg-streamer
systemctl enable spookybox; systemctl start spookybox
