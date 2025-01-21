This program is still being worked on.

Using the ascom driver built into most GoTo-Telescopes, the technology is still in works but it will allow you to make your telescope more effective in daylight spotting.

What is what:

SideFunction/ <- this folder contains functions that are used in multiple other files, they just make everything a bit more easy.

AscomREAD.py <- used for debugging, check what functions your telescope allows.
calculateAltPlane.py <- ChatGPT made demo for tracking airplanes using the opensky API.
CoordinateFollower.py <- handy file to quickly make the telescope slew to wather coordinare you want.
main.py <- Demo on being able to go to any coordinate clicked within the window, simulates my actual window where the telescope is in front off, calculates what objects are visible from within thos restrictions.
ScndSpeedDemo.py <- File with most important function and some testing
