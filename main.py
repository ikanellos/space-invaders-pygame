#!/usr/bin/python

############################################################
## IMPORTS ##
import pygame
import random
import math

# Namespace imports
from pygame import mixer
############################################################
## FUNCTIONS ##
# I have collapsed the draw function into a single 
# one taking coordinates and image objects as input
def draw_sprite(x, y, image):
    '''Draw a sprite at x,y'''
    global screen
    screen.blit(image, (x, y))
#--------------------------------------------------------- #
def render_score(x, y, score_display, score, ships):
    global screen
    global SCREEN_WIDTH
    rendered_score = score_display.render(f"Score: {score}", True, (255, 255, 255))
    size_x, size_y = score_display.size(f"Score: {score}")
    screen.blit(rendered_score, (SCREEN_WIDTH - (size_x + 20),10))
    # Render Number of destroyed ships
    rendered_ships = score_display.render(f"Ships destroyed: {ships}", True, (255,255,255))
    screen.blit(rendered_ships, (10,10))
#--------------------------------------------------------- #
# Render Game over text
def game_over_render(game_over_display_font, game_over_score_font, score, ships, chars_inserted = []):
    global screen
    global SCREEN_HEIGHT
    global SCREEN_WIDTH
    rendered_game_over = game_over_display_font.render("GAME OVER", True, (255, 105, 105))
    size_x, size_y = game_over_display_font.size("GAME OVER")
    screen.blit(rendered_game_over, ((SCREEN_WIDTH/2 - size_x/2), (SCREEN_HEIGHT/2 - size_y/2 - 100)))
    rendered_game_over_score = game_over_score_font.render(f"Score: {score} - Enemies Killed:{ships}", True, (255,100,100))
    score_size_x, score_size_y = game_over_score_font.size(f"Score: {score} - Enemies Killed:{ships}")
    screen.blit(rendered_game_over_score, ((SCREEN_WIDTH/2 - score_size_x/2), (SCREEN_HEIGHT/2 + size_y/2)+score_size_y - 100))
    # Render character input
    rendered_insert_initials = game_over_score_font.render("INSERT INITIALS", True, ((255, 105, 105)))
    initials_size_x, initials_size_y = game_over_score_font.size("INSERT INITIALS")
    # Center on x and 
    screen.blit(rendered_insert_initials, ((SCREEN_WIDTH/2 - initials_size_x/2), (SCREEN_HEIGHT/2 + size_y/2 + score_size_y/2) + initials_size_y-50))
    # Characters input so far. Show empty spaces for characters not inserted
    render_string = "_ _ _" if not chars_inserted else " ".join(chars_inserted)
    if chars_inserted and len(chars_inserted) < 3:
        render_string += " _" * (3-len(chars_inserted))
    rendered_initials = game_over_score_font.render(render_string, True, ((255, 105, 105)))
    added_inits_x, added_inits_y = game_over_score_font.size(render_string)
    screen.blit(rendered_initials, ((SCREEN_WIDTH/2 - added_inits_x/2), (SCREEN_HEIGHT/2 + size_y/2 + score_size_y/2 + initials_size_y/2) + added_inits_y-30))
#--------------------------------------------------------- #
def show_high_scores(game_over_score_font, score_list):
    '''Display scores from high score file'''
    global screen
    global SCREEN_HEIGHT
    global SCREEN_WIDTH

    rendered_high_scores = game_over_score_font.render("HIGH SCORES", True, (255, 255, 255))
    high_scores_x, high_scores_y = game_over_score_font.size("HIGH SCORES")
    screen.blit(rendered_high_scores, ((SCREEN_WIDTH/2-high_scores_x/2), (high_scores_y)))

    # Display high scores
    for offset, high_scorer in enumerate(score_list):
        rendered_high_scorer = game_over_score_font.render(f"{high_scorer[0]}: {high_scorer[1]}", True, (255, 255, 255))
        high_scorer_x, high_scorer_y = game_over_score_font.size(f"{high_scorer[0]}: {high_scorer[1]}")
        screen.blit(rendered_high_scorer, ((SCREEN_WIDTH/2-high_scorer_x/2), (high_scores_y + 10 + high_scorer_y * (offset+1))))        

    # Print restart message
    restart_msg = game_over_score_font.render("Continue? y/n", True, (255, 255, 255))
    restart_msg_x, restart_msg_y = game_over_score_font.size("Continue? y/n")
    screen.blit(restart_msg, ((SCREEN_WIDTH/2-restart_msg_x/2), (SCREEN_HEIGHT-restart_msg_y)))

#--------------------------------------------------------- #
def get_high_scores(high_score_file = 'high_scores.txt'):
    '''Returns a sorted dictionary of high scores, read from high_scores.txt'''
    scorers_list = []
    # Read high scores from file and display them
    with open(high_score_file, 'r') as f:
        for line in f:
            line = line.strip()
            scorer, score = line.split("\t")
            scorers_list.append((scorer, int(score)))
    return scorers_list # this should be read in sorted order
# -------------------------------------------------------- #
def write_high_scores(score_list, output_file='high_scores.txt'):
    '''Writes the sorted dictionary of scores to a file'''
    file_handler = open(output_file, 'w')
    for item in score_list:
        file_handler.write(f"{item[0]}\t{item[1]}\n")
    file_handler.close()
#--------------------------------------------------------- #
def collision(enemy_x, enemy_y, other_x, other_y):
    '''Detect collision between enemy and bullet'''
    global SPRITE_DIAGONAL_HALF
    x_sqdiff = (other_x - enemy_x) ** 2
    y_sqdiff = (other_y - enemy_y) ** 2
    distance = math.sqrt(x_sqdiff + y_sqdiff)
    # Check if distance is less than half of the enemy sprite diagonal
    # --> this would correspond to a circle w/ center of the sprite as center
    # and a radius of the diagonal.
    # Enemy sprite: 64x64 square, so by pythagoras, 
    # diagonal = sqrt(64^2 + 64^2) ~ 90. So, from the center of the sprite 
    # we have diagonal / 2 ~ 45
    return True if distance < SPRITE_DIAGONAL_HALF else False
############################################################
# INITIALIZATIONS

# --------- CONSTANTS ------------- #
# Set default size for sprites
DEFAULT_SPRITE_SIZE = (64,64)
DEFAULT_BULLET_SIZE = (40,40)
# Screen width and heiht
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
# HALF DIAGONAL OF SPRITE - see collision function
SPRITE_DIAGONAL_HALF = int(math.sqrt(2 * (DEFAULT_SPRITE_SIZE[0]**2))/2)
# NUMBER OF ENEMIES
NUM_ENEMIES = 6

# List holding initilals inserted by the user after game over
initials = []
# --------------------------------- #
# ------------ GAME INIT ---------- #
# Initialize the game to have access to all its modules
# NOTE: this is  required as an initialization everytime
# we use pygame
pygame.init()

# Now we need to create an initial screen. 
# This is done by accessing the respecitve module inside pygame
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT)) # mode needs a tuple with the height/width of screen
# ΝΟΤΕ: 0,0 of the window is at the top left corner
# --------------------------------- #
# ------ LOAD & DEFINE IMAGES ----- #
#BACKGROUND
background = pygame.image.load("earth.jpg")
# Resize to window size
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
# Set window title
pygame.display.set_caption("Space Invaders")
# ------- PROBLEM: My ICON WON'T LOAD ----------------------------- #
# Add an icon to the game window - this command here loads the image
icon = pygame.image.load('ufo.png')
# Not to add the image to the screen
pygame.display.set_icon(icon)

# Load player image
player_image = pygame.image.load('space-invaders.png')
player_image = pygame.transform.scale(player_image, DEFAULT_SPRITE_SIZE)

# Load enemy
enemy_image = pygame.image.load('ufo.png')
enemy_image = pygame.transform.scale(enemy_image, DEFAULT_SPRITE_SIZE)

# Bullet image
bullet_image = pygame.image.load('bullet.png')
bullet_image = pygame.transform.scale(bullet_image, (40,40))
# ----------------------------------------------------------------- #
# SOUNDS

# Backing track
mixer.music.load("bg_music.mp3")
# Play it throughout
mixer.music.play(-1) # -1 is to loop the music
# Bullet sound
bullet_sound = mixer.Sound("shot.mp3")
# Explosion sound
explosion_sound = mixer.Sound("explosion.mp3")
# Game over
game_over_sound = mixer.Sound("game_over.mp3")
# ----------------------------------------------------------------- #
# ---------- INITIAL POSITIONS AND MOVEMENT VARIABLES ------------- #
# Player image initial location
player_x     = 370 # this is about the middle of the screen
player_y     = 480
# Setup player movement parameters
dx = 0
dy = 0

enemy_x  = []
enemy_y  = []
enemy_dx = []
enemy_dy = []
# This will hold an offset per enemy, so that
# they respawn lower each time to make the game more difficult
enemy_vertical_offset = []
# ENEMY LIST initialization
for i in range(NUM_ENEMIES):
    # Enemy image initial (random) location
    enemy_x.append(random.randint(0,SCREEN_WIDTH-enemy_image.get_width())) # this is about the middle of the screen
    enemy_y.append(random.randint(int(SCREEN_HEIGHT*0.01),int(SCREEN_HEIGHT*0.3)))
    # Setup initial enemy movement parameters
    enemy_dx.append(0.3)
    enemy_dy.append(enemy_image.get_height() / 3)
    enemy_vertical_offset.append(0)
# Initial bullet position at spaceship position
bullet_x = player_x + 12
bullet_y = 480-bullet_image.get_height()
# Bullet movement parameter
bullet_dy = -1
# NOTE: bullet doesn't move on the x-axis.
# NOTE: we allow 1 bullet at a time on the screen
# Bullet visibility
bullet_visible = False
# ----------------------------------------------------------------- #
# GAME STATISTICS INITIALIZATION
score = 0
ships_destroyed = 0
score_display = pygame.font.Font("freesansbold.ttf", 20)
# Score coordinates
score_x = SCREEN_WIDTH-40
score_y = 10
# Game over text
game_over_font = pygame.font.Font("freesansbold.ttf", 64)
game_over_score_font = pygame.font.Font("freesansbold.ttf", 32)
# ----------------------------------------------------------------- #
# GAME LOOP STARTS HERE ONWARDS

# Game state flags
game_over = False
game_over_sounded = False
game_running = True
display_scores = False
await_restart  = False
while game_running:
    # Set the color of the screen. Draw this initiallt to not
    # draw over anything else that should appear on the screen
    screen.fill((0,0,0)) # <- takes an rbg tuple
    # Draw background image
    screen.blit(background, (0,0))

    # In each game a series of events happen.
    #  We need to read them and handle them accordingly 
    for event in pygame.event.get():
        # If the close button is pressed, quit
        if event.type == pygame.QUIT:
            game_running = False

        # Handle keyboard input
        if event.type == pygame.KEYDOWN:

            # If we are at game over state
            # get the initials
            if game_over:
                # The key will be a number
                key_pressed = event.key
                # ... the range here is a-z
                if key_pressed in range(97, 123):
                    # Add the character to the initials list
                    initials.append(chr(key_pressed))

                    if len(initials) == 3:
                        # Write score to file
                        scores_list = get_high_scores('high_scores.txt')
                        # keep 10 scores at maximum. completely rewrite the file if a new score enters
                        lowest_score = min([int(score[1]) for score in scores_list]) if scores_list else 0
                        # Add to dictionary
                        if not scores_list or score >= lowest_score:
                            current_name = "".join(initials)
                            scores_list.append((current_name, score))
                            # Rewrite file
                            scores_list.sort(key = lambda x: x[1], reverse=True)
                            # Write up to the 15th element only - keep the list short
                            write_high_scores(scores_list[:10])

                        # Update game state
                        display_scores = True

                elif key_pressed == pygame.K_BACKSPACE and initials:
                    initials.pop()

            if display_scores:
                # Quit or restart
                if event.key == pygame.K_n:
                    game_running = False
                if event.key == pygame.K_y:
                    # Reinitialize all game variables
                    display_scores = False
                    game_over = False
                    game_running = True
                    score = 0 
                    initials = []
                    await_restart = False
                    ships_destroyed = 0 
                    # Re-initialize enemies
                    enemy_x  = []
                    enemy_y  = []
                    enemy_dx = []
                    enemy_dy = []
                    # This will hold an offset per enemy, so that
                    # they respawn lower each time to make the game more difficult
                    enemy_vertical_offset = []
                    # ENEMY LIST initialization
                    for i in range(NUM_ENEMIES):
                        # Enemy image initial (random) location
                        enemy_x.append(random.randint(0,SCREEN_WIDTH-enemy_image.get_width())) # this is about the middle of the screen
                        enemy_y.append(random.randint(int(SCREEN_HEIGHT*0.01),int(SCREEN_HEIGHT*0.3)))
                        # Setup initial enemy movement parameters
                        enemy_dx.append(0.3)
                        enemy_dy.append(enemy_image.get_height() / 3)
                        enemy_vertical_offset.append(0)                    


            '''
            # Force game over for testing
            if event.key == pygame.K_q:
                game_over = True
            '''
            # If escape is pressed, exit windoe
            if event.key == pygame.K_ESCAPE:
                game_running = False
            # Check actual key
            if event.key == pygame.K_LEFT:
                # If left arrow set speed & direction
                dx = -0.4
            if event.key == pygame.K_RIGHT:
                # If right arrow set speed & direction
                dx = 0.4
            if event.key == pygame.K_SPACE and not bullet_visible:
                # If space, fire bullet, unless a bullet is already on the screen
                bullet_visible = True
                # Set x coordinate of bullet at spaceship position
                bullet_x = player_x + 12
                bullet_y = 480-bullet_image.get_height()
                # Play bullet sound
                bullet_sound.play()

        # Stop movement as long as we don't have another key pressed
        if event.type == pygame.KEYUP:
            # Stop movement speed if we leave key and no other speed key is pressed
            if event.key == pygame.K_LEFT and dx != 0.4:
                dx = 0
            if event.key == pygame.K_RIGHT and dx != -0.4:
                dx = 0
                

    # -------------------------------------------------------------- #
    # UPDATE movements that happen without any condition
    # Update player coordinates
    player_x += dx
    player_y += dy
    # Update enemy coordinates
    for i in range(NUM_ENEMIES):
        # Check if enemy collides with player, or goes below player position
        # If so, set game over parameter
        if enemy_y[i] > player_y or collision(enemy_x[i], enemy_y[i], player_x, player_y):
            game_over = True 
            if not game_over_sounded:
                pygame.mixer.music.stop()
                game_over_sound.play()
                game_over_sounded = True
            # No need to continue on enemy loop
            break

        # UPDATE enemy movements
        enemy_x[i]  += enemy_dx[i]
        # Constrain enemy movement inside boundaries & move downwards
        enemy_x[i] = 0 if (enemy_x[i] <= 0) else enemy_x[i]
        enemy_x[i] = (SCREEN_WIDTH-enemy_image.get_width()) \
                    if (enemy_x[i] >= (SCREEN_WIDTH-enemy_image.get_width())) else enemy_x[i]
        # Change direction if at boundary
        enemy_dx[i] = -enemy_dx[i] if (enemy_x[i] == 0 or enemy_x[i] == (SCREEN_WIDTH-enemy_image.get_width())) \
                    else enemy_dx[i]
        enemy_y[i]  = enemy_y[i] + enemy_dy[i] \
                    if (enemy_x[i] == 0 or enemy_x[i] == (SCREEN_WIDTH-enemy_image.get_width())) else enemy_y[i]


    # Update bullet coordinate & visibility
    bullet_y = bullet_y + bullet_dy if bullet_visible else bullet_y
    if (bullet_y <= 0 and bullet_visible):
        bullet_visible = False
    # -------------------------------------------------------------- #
    # UPDATE movements/positions conditionally - ENEMY MOVEMENT WAS
    # MOVED TO THE ENEMY unconditional movement update to avoid multiple
    # for loops

    # Constrain player movements inside boundaries
    player_x = 0 if (player_x <= 0) else player_x
    player_x = (SCREEN_WIDTH-player_image.get_width()) \
                if player_x >= (SCREEN_WIDTH-player_image.get_width()) else player_x
    # -------------------------------------------------------------- #
    # COLLISION DETECTION & UPDATES
    if bullet_visible and not game_over:
        for i in range(NUM_ENEMIES):
            if collision(enemy_x[i], enemy_y[i], bullet_x, bullet_y):
                # Play explosion sound
                explosion_sound.play()
                # Reset invisibility of bullet - coordinates are set at new space bar press
                bullet_visible = False
                # Reset enemy appearance
                enemy_vertical_offset[i] += 10
                enemy_x[i] = random.randint(0,SCREEN_WIDTH-enemy_image.get_width())
                # Also add extra offset on respawn
                enemy_y[i] = random.randint(int(SCREEN_HEIGHT*0.01) + enemy_vertical_offset[i],int(SCREEN_HEIGHT*0.3) + enemy_vertical_offset[i])

                # Score increment
                score += 5
                # Ship count increment
                ships_destroyed += 1
                # Increase enemy speed
                enemy_dx[i] = enemy_dx[i] + 0.02 if (enemy_dx[i] > 0) else enemy_dx[i] - 0.02
                enemy_dy[i] += 0.2
                # Slightly increse bullet speed
                # NOTE: I decided to keep bullet speed constant
                # bullet_dy -= 0.02
    
    # -------------------------------------------------------------- #
    # DRAW SPRITES    
    draw_sprite(player_x, player_y, player_image) # player
    # Redraw enemies - except if we are in a game state that doesn't require it
    if not game_over:
        for i in range(NUM_ENEMIES):
            draw_sprite(enemy_x[i], enemy_y[i], enemy_image)
    elif game_over and not display_scores:
        game_over_render(game_over_font, game_over_score_font, score, ships_destroyed, initials)
    elif display_scores:
        if not await_restart:
            score_dictionary = get_high_scores('high_scores.txt')

        show_high_scores(game_over_score_font, score_dictionary)
        await_restart = True

    # Draw bullet
    if bullet_visible and not game_over:
        high_score_dict = get_high_scores()
        draw_sprite(bullet_x, bullet_y, bullet_image)
    
    # Render Score
    if not game_over:
        render_score(score_x, score_y, score_display, score, ships_destroyed)

    # To see all (re-)drawings, we need to update the display
    pygame.display.update()

print ("\n##### ----- BYE! ----- #####\n")