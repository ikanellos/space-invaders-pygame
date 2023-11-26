# Space Invaders

This is my code-along and implementation of a space invaders game using pygame, found at
https://www.youtube.com/watch?v=FfWpgLFMI7w&ab_channel=freeCodeCamp.org.

My code is based on the above, but differs in code structure and certain parts of the logic. 

#### Key differences in Code Structure:
- Unified draw function for any type of sprite. Code is made more compact.
- Sprite positions are dynamically calculated using get_width() & get_height().
- Sounds are loaded at initialization & only played when needed. Original code re-instantiates a sound object whenever a sound needs to be played.
- Enemies and Bullets stop being redrawn after game over. Original implementation 
  simply moved them out of the viewport.
- Enemies increase in speed after being destroyed. Also they spawn ever more closely to the player

#### Minor code variable differences:
- Constants have been moved to the top of the code and are used throughout with their name instead of value.
- Bullet state changed from string to bullet_visibility which is a Boolean.

#### Game Logic / Presentation differences:
- Different images for background, aliens, bullets.
- Added enter initials and high score display after game over (top 10 scorers are kept on a file)
- After game over and initials, player has the option to restart or quit

#### Sounds & Sprites
Have been downloaded from freeware sites.








