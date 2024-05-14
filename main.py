import pygame
import random
import sys
import os
import time
import asyncio
from pygame.locals import *

async def main():
    WINDOWWIDTH = 600
    WINDOWHEIGHT = 600
    TEXTCOLOR = (255, 255, 255)
    BACKGROUNDCOLOR = (128, 128, 128)  # Changed to grey
    FPS = 120
    BADDIEMINSIZE = 10
    BADDIEMAXSIZE = 40
    BADDIEMINSPEED = 8
    BADDIEMAXSPEED = 8
    ADDNEWBADDIERATE = 15
    PLAYERMOVERATE = 5
    count = 3

    def terminate():
        pygame.quit()
        sys.exit()

    def waitForPlayerToPressKey():
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:  # escape quits
                        terminate()
                    return

    def playerHasHitBaddie(playerRect, baddies):
        for b in baddies:
            if playerRect.colliderect(b['rect']):
                return True
        return False

    def drawText(text, font, surface, x, y, bgcolor=None, smallfont=False, centered=False):
        textobj = font.render(text, 1, TEXTCOLOR)
        textrect = textobj.get_rect()
        if centered:
            textrect.center = (x, y)
        else:
            textrect.topleft = (x, y)
        if bgcolor:
            pygame.draw.rect(surface, bgcolor, textrect)  # Background color
        surface.blit(textobj, textrect)

    # Set up pygame, the window, and the mouse cursor
    pygame.init()
    mainClock = pygame.time.Clock()
    windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('car race')
    pygame.mouse.set_visible(False)

    # Fonts
    font = pygame.font.SysFont(None, 30)
    smallfont = pygame.font.SysFont(None, 25)  # Small font

    # Sounds
    gameOverSound = pygame.mixer.Sound('music/crash.wav')
    pygame.mixer.music.load('music/car.wav')
    laugh = pygame.mixer.Sound('music/laugh.wav')

    # Images
    playerImage = pygame.image.load('image/car6.png')
    car3 = pygame.image.load('image/car1.png')
    car4 = pygame.image.load('image/car7.png')
    playerRect = playerImage.get_rect()
    baddieImage = pygame.image.load('image/car8.png')
    sample = [car3, car4, baddieImage]
    wallLeft = pygame.image.load('image/left.png')
    wallRight = pygame.image.load('image/right.png')

    # Define lane properties
    LANE_WIDTH = 30
    LANE_COLOR = (255, 255, 255)
    LANE_SPACING = 50

    def showHomeScreen():
        windowSurface.blit(backgroundImage, (0, 0))
        drawText('Press any key to start and hit ESC to quit the game', font, windowSurface, WINDOWWIDTH / 2, WINDOWHEIGHT - 50, centered=True)  # Centered
        pygame.display.update()
        waitForPlayerToPressKey()

    # Load background image
    backgroundImage = pygame.image.load('image/home.jpg')
    backgroundImage = pygame.transform.scale(backgroundImage, (WINDOWWIDTH, WINDOWHEIGHT))

    showHomeScreen()

    zero = 0
    if not os.path.exists("data/save.dat"):
        with open("data/save.dat", 'w') as f:
            f.write(str(zero))

    with open("data/save.dat", 'r') as v:
        topScore = int(v.readline())

    while count > 0:
        # Start of the game
        baddies = []
        score = 0
        playerRect.topleft = (WINDOWWIDTH / 2, WINDOWHEIGHT - 50)
        moveLeft = moveRight = moveUp = moveDown = False
        reverseCheat = slowCheat = False
        baddieAddCounter = 0
        pygame.mixer.music.play(-1, 0.0)

        while True:  # The game loop
            score += 1  # Increase score

            # Store the rectangles of existing baddies
            baddie_rects = [b['rect'] for b in baddies]

            for event in pygame.event.get():
                if event.type == QUIT:  # or press esc
                    terminate()

                if event.type == KEYDOWN:
                    if event.key == ord('z'):
                        reverseCheat = True
                    if event.key == ord('x'):
                        slowCheat = True
                    if event.key == K_LEFT or event.key == ord('a'):
                        moveRight = False
                        moveLeft = True
                    if event.key == K_RIGHT or event.key == ord('d'):
                        moveLeft = False
                        moveRight = True
                    if event.key == K_UP or event.key == ord('w'):
                        moveDown = False
                        moveUp = True
                    if event.key == K_DOWN or event.key == ord('s'):
                        moveUp = False
                        moveDown = True

                if event.type == KEYUP:
                    if event.key == ord('z'):
                        reverseCheat = False
                        score = 0
                    if event.key == ord('x'):
                        slowCheat = False
                        score = 0
                    if event.key == K_ESCAPE:
                        terminate()

                    if event.key == K_LEFT or event.key == ord('a'):
                        moveLeft = False
                    if event.key == K_RIGHT or event.key == ord('d'):
                        moveRight = False
                    if event.key == K_UP or event.key == ord('w'):
                        moveUp = False
                    if event.key == K_DOWN or event.key == ord('s'):
                        moveDown = False

            # Add new baddies at the top of the screen
            if not reverseCheat and not slowCheat:
                baddieAddCounter += 1
            if baddieAddCounter == ADDNEWBADDIERATE:
                baddieAddCounter = 0
                baddieSize = 30
                newBaddieRect = pygame.Rect(random.randint(140, 485), 0 - baddieSize, 23, 47)
                if not any(bad_rect.colliderect(newBaddieRect) for bad_rect in baddie_rects):
                    newBaddie = {'rect': newBaddieRect,
                                 'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
                                 'surface': pygame.transform.scale(random.choice(sample), (23, 47)),
                                 }
                    baddies.append(newBaddie)
                    sideLeft = {'rect': pygame.Rect(0, 0, 126, 600),
                                'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
                                'surface': pygame.transform.scale(wallLeft, (126, 599)),
                                }
                    baddies.append(sideLeft)
                    # Adjust the position of the right side wall
                    sideRight = {'rect': pygame.Rect(497, 0, 125, 600),
                                 'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
                                 'surface': pygame.transform.scale(wallRight, (126, 599)),
                                 }
                    baddies.append(sideRight)

            # Move the player around
            if moveLeft and playerRect.left > 0:
                playerRect.move_ip(-1 * PLAYERMOVERATE, 0)
            if moveRight and playerRect.right < WINDOWWIDTH:
                playerRect.move_ip(PLAYERMOVERATE, 0)
            if moveUp and playerRect.top > 0:
                playerRect.move_ip(0, -1 * PLAYERMOVERATE)
            if moveDown and playerRect.bottom < WINDOWHEIGHT:
                playerRect.move_ip(0, PLAYERMOVERATE)

            for b in baddies:
                if not reverseCheat and not slowCheat:
                    b['rect'].move_ip(0, b['speed'])
                elif reverseCheat:
                    b['rect'].move_ip(0, -5)
                elif slowCheat:
                    b['rect'].move_ip(0, 1)

            for b in baddies[:]:
                if b['rect'].top > WINDOWHEIGHT:
                    baddies.remove(b)

            # Draw the game world on the window
            windowSurface.fill(BACKGROUNDCOLOR)

            # Draw the dotted lines on the road
            for y in range(0, WINDOWHEIGHT, LANE_SPACING):
                pygame.draw.line(windowSurface, LANE_COLOR, (WINDOWWIDTH / 2, y), (WINDOWWIDTH / 2, y + LANE_WIDTH), 2)

            windowSurface.blit(playerImage, playerRect)

            for b in baddies:
                windowSurface.blit(b['surface'], b['rect'])

            # Draw the score and top score
            drawText('Score: %s' % (score), smallfont, windowSurface, 20, 20, (0, 0, 0), True)  # Extreme left with background color and small font
            drawText('Rest Life: %s' % (count), smallfont, windowSurface, 20, 40, (0, 0, 0), True)  # Extreme left with background color and small font
            drawText('Top Score: %s' % (topScore), smallfont, windowSurface, WINDOWWIDTH - 150, 20, None, True)  # Extreme right with small font

            pygame.display.update()

            # Check if any of the cars have hit the player
            if playerHasHitBaddie(playerRect, baddies):
                if score > topScore:
                    with open("data/save.dat", 'w') as g:
                        g.write(str(score))
                    topScore = score
                break

            await asyncio.sleep(0)  # Allow other tasks to run

        # "Game Over" screen
        pygame.mixer.music.stop()
        count -= 1
        gameOverSound.play()
        await asyncio.sleep(1)
        if count == 0:
            laugh.play()
            drawText('Game over', font, windowSurface, WINDOWWIDTH / 2, WINDOWHEIGHT / 2, centered=True)  # Centered
            drawText('Press any key to play again.', font, windowSurface, WINDOWWIDTH / 2, (WINDOWHEIGHT / 2) + 30, centered=True)  # Centered
            pygame.display.update()
            await asyncio.sleep(2)
            waitForPlayerToPressKey()
            count = 3
            gameOverSound.stop()

asyncio.run(main())
