Smoothie Factory
======

Smoothie Factory is inspired by Rat-Poker, a Microsoft game from 1997. Video: http://www.youtube.com/watch?v=viKON2PMH0g

Purpose: use pygame, know how to make UI menus, play a game with GF

Concept: Fruits appear from a door, and travel on a path throughout the kitchen. You're in charge of ordering fruits according to certain recipes, so that when they reach the chef, they can be processed into a smoothie.




Phases
=====

phase 1
- 1 combo (3 in a row)
- 1 trap
- square path
- no menu


phase 2
- UI menus, configs (frame rate, sound, controls)
- different combos
- fruits decay over time (rotten fruits bring less points)
- conditional paths (e.g. blues go right, others go left)
- multiple traps (store multiple rats, teleport rats)
- 2-player: shared screen, one player controls traps inside the loop, the other controls traps outside the loop (so when there's a fork in the path, only one player can handle a branch but not the other)
