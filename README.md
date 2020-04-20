GearHead Caramel
================

GearHead Caramel- Third game in the GearHead series, first written in Python.

To install, just unzip the standalone distribution to a convenient place and
double click "ghcaramel". To do a DIY installation from source code, see the
instructions below.

![Screenshot](image/screenshot.png)

ABOUT
=====

The first scenario for GearHead Caramel is Winter Mocha. Set a few months
after the Typhon Incident, you are invited to take part in a charity mecha
tournament at the newly constructed Mauna Arena.

This is an early alpha release- there are tons of things that aren't finished
yet. However, it's a fun little scenario, and will show you some of the new
things that GearHead Caramel can do.

Note: If you have trouble running ghcaramel on MacOS, you may need to set
the executable permission on the file (chmod a+x ghcaramel) or configure
MacOS gatekeeper to allow it to run.

CONTROLS
========

Most things in GearHead Caramel are done using the mouse, but there
are keyboard shortcuts for some. 
Note that commands are case sensitive- "Q" is different from "q".

Left click: Move to spot

Right click: Open skills menu during exploration

c: Center the screen on the party/active character

Q: Quit the game.

H: Open the Field HQ (Exploration mode only)

m: Browse memos (Exploration mode only)

In the attack/skill/EWar interface, click the name of your weapon/skill/program
to change to a different one. You can
scroll through weapons and attack options using the mouse wheel or the 
arrow keys.

In the combat movement interface, click the movemode to change movemode.


BUILDING FROM SOURCE
====================

Things have gotten a bit more complicated since the last time I updated
this file. To build GearHead Caramel from source, first you will need to
install Python3. After that you need to install the PyGame, Numpy, and
Cython packages. The easiest way to install these is with "pip". You may
also need to install a C compiler for Cython; see the Cython page for
details.

  https://www.python.org/

The first time it's run, the game will create a "ghcaramel" folder in your
home directory and place a configuration file there. This is where all of your
characters and saved games are stored, in case you want to delete them or
make backups. The configuration file can be edited in any text editor.
