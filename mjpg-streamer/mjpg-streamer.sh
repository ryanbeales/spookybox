#!/bin/bash
/usr/local/bin/mjpg_streamer -i "/usr/local/lib/mjpg-streamer/input_raspicam.so -rot 180 -fps 30" -o "/usr/local/lib/mjpg-streamer/output_http.so -w /usr/local/share/mjpg-streamer/www -p 8080"


