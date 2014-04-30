Smoothie Factory
======

Smoothie Factory is inspired by Rat-Poker, a Microsoft game from 1997. Video: http://www.youtube.com/watch?v=viKON2PMH0g

Purpose: use pygame, know how to make UI menus, play a game with GF

Concept: Fruits appear from a door, and travel on a conveyor path throughout the factory. You're in charge of ordering fruits according to certain recipes, so that when they reach the blender, they can be processed into a smoothie. Press space to capture/release a fruit at a capture station.



License
====

GPL



Install and run
====

For Python 3:
- python 3
- python3-yaml
- pygame

For Python 2.7
- python 2.7
- yaml http://pyyaml.org/wiki/PyYAML
- pygame
- replace configparser by ConfigParser, in config.py

Then: python smofac.py


Phases
=====

phase 1
- 2 recipes (3 and 4 in a row)
- 4 fruit types (R=strawb, G=kiwi, B=blueberry, J=banana)
- 1 trap
- square path
- 2 levels (each won when 8 smoothies have been made) 
- basic transitions between levels
- player score carried along levels
- pre-game menu boxes: 'play game' and 'quit'
- executable (py2exe for Windows, ??? for Linux)


phase 2
- fancier pre-game UI menus: 'config' and '2 player', with img background
- config for frame rate, sound, and controls 
- 2-player: shared screen, one player controls traps inside the loop, the other controls traps outside the loop (so when there's a fork in the path, only one player can handle a branch but not the other)
- sound effects and music
- 6 recipes
- multiple types of traps (store multiple fruits, teleport fruits to another trap's cell)
- power-up: slow down the conveyor 
- pause the game


phase 3
- fruits decay over time (rotten fruits bring less points)?
- more power-ups: turn all of the fruits in an area into strawbs, or the blender accepts the next 5 fruits whatever they are, or the rotten fruits are cleaned from the conveyor
- conditional paths (e.g. blues go right, others go left)?
- bigger fruits bring more points? (Cf rats with a small 'plus' bag)
- polishing at the level of popcap
- embedded tutorial (hardcode an easy order at which the fruit spawns?)
- story? Young kid wants to become rich making the best smoothies in the world. S/he starts making smoothies in the garage, then buys small factory, then large factory.
- pacing within and between levels
- playtests
