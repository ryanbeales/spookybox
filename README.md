# What is this?
It's a spooky box? Have a look at what this does by clicking on this image:

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/fMFsZu-fMfk/0.jpg)](https://www.youtube.com/watch?v=fMFsZu-fMfk)

# Running:
These are my rough notes so I remember what to do for Halloween 2022.

1. Get a raspberry pi and camera module
1. 3D print the freecad base model
1. Acquire a box, of the exact same dimensions... Like I said, these are my notes.
1. Git clone this in to /home/pi/src/
1. Run `system_packages.sh` to install everything. Curse when it doens't work or I've forgotten something.
1. `pip3 install -r requirements.txt `
1. Copy service files in services/ to /etc/systemd/system/
1. `systemctl daemon-reload`
1. `systemctl enable pigpiod; systemctl start pigpiod`
1. `systemctl enable spookybox; systemctl start spookybox`
