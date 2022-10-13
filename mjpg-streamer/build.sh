#~/bin/bash

apt-get install cmake libjpeg8-dev gcc

curl -fsSLO --compressed --retry 3 --retry-delay 10 https://github.com/jacksonliam/mjpg-streamer/archive/master.tar.gz && mkdir /mjpg && tar xzf master.tar.gz -C /mjpg

cd  /mjpg/mjpg-streamer-master/mjpg-streamer-experimental

make 

make install
