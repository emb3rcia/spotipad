# spotipad
Spotify control micropad made for hackpad.hackclub.com
# PCB
DSDDD
# Case
dsadwa
# Code
Right now, the code is sloppy and probably won't work. The reason is that I don't have the microcontroller yet, so I don't know how to check if the code works, and there's nothing I hate more than writing code blindly without the ability to test it. The current code is more a visualization of my idea:
Spotipad connects normally via USB
Keys and turn-knob send media keys (volume up/down, mute, next/previous track, pause/play).
The screen has 3 options (currently only 1 is “visualized” via demo code).
1. Connect to a locally hosted Flask server that checks the currently played track name and author and sends it via USB Serial Data.
2. Displays text set in config file/GUI (TO:DO)
3. Displays 128x32 image set in config file/GUI (TO:DO)
# Background
I have wanted to make something like this for months now. My idea arose when I saw the death of Spotify's "CarThing" which people used as a desk accessory. I didn't have CarThing, so I couldn't use it in this way, so I tried making an improvised one using an old Android phone I had lying around and some live wallpaper app. It didn't work well. Now, when I saw an email in my inbox about hackclub, and saw that I could make a micropad for basically free, I was euphoric. I like to do stuff. I have many ideas for some hardware stuff but don't have funds to bring them to life. Sadly, I discovered hackclub at the end of this "highway." If there will be another "edition," I will do all hands on deck to fully participate. This creation (at least the first iteration) was made in 1 night after 1 too many caffeine capsule (don't do this; it is bad for you 😇). It was also the first time I did PCB and the first time I 3D-designed something that will really be sent to be printed.
