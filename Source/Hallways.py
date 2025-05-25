import pygame
import random
import math

import numpy as np

pygame.init()
screenWidth = 800
screenHeight = 600
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('Hallways')

#fps display
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 25)
def displayFPS(screen):
    fps = round(clock.get_fps(), 1)
    fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))  # White text
    screen.blit(fps_text, (10, 10))  # Top-left corner with slight padding

#debug toggles and preferences
debug1 = False       #display fps

debug2 = True       #toon shader effect
debug3 = True      #grain effect

allow1 = False      #sprint on shift
allow2 = False      #walk through walls

#-----------------------------------------------------------------------------------------------------------------------------------------

class Grid():
    def __init__(self):
        self.tilesize = 30

        #filled up with rects for acces in line intersection using pygames clipline
        self.rects = []

        self.grid = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,0,1,1,1,0,0,0,0,0,1,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,1,1,1,1,0,1,1,1,0,1,1,1],
            [1,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,1],
            [1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,0,0,0,0,1],
            [1,0,0,1,0,0,0,1,0,0,0,1,0,0,1,1,1,1,1,1],
            [1,0,0,1,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,1],
            [1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,1,1,0,1,1,1,0,1,1,0,0,0,1,0,0,0,1],
            [1,1,1,1,0,0,0,1,0,0,0,1,1,0,1,1,0,0,0,1],
            [1,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1],
            [1,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,1,0,1,1],
            [1,0,0,1,1,0,1,1,1,1,1,1,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]

        #initialize grid rects
        self.rects = []

        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[x][y] == 1:
                    topleft = (self.tilesize * y, self.tilesize * x)
                    rect = pygame.Rect(topleft[0], topleft[1], self.tilesize, self.tilesize)
                    pygame.draw.rect(screen, (150, 150, 150), rect)
                    self.rects.append(rect)
        
class Player():
    def __init__(self, pos):

        self.pos = pos
        self.angle = 60

        self.fov = 90
        self.verticalFov = 7200
        self.numOfRays = 100
        self.raysWidth = screenWidth/self.numOfRays
        self.rayLength = 180

        self.speed = 50
        self.walkSpeed = 50
        self.sprintSpeed =self.walkSpeed * 2.5
        self.rotationSpeed = 0.15

        self.width = 10

    def move(self, deltaTime, vDir, grid):
        #rotate vDir by angle for ralative to player
        angleRad = math.radians(self.angle)
        xRot = vDir[0] * math.cos(angleRad) - vDir[1] * math.sin(angleRad)
        yRot = vDir[0] * math.sin(angleRad) + vDir[1] * math.cos(angleRad)
        vRel = (xRot, yRot)

        #movement without collision
        nextPos = (self.pos[0] + vRel[0] * deltaTime * self.speed, self.pos[1] + vRel[1] * deltaTime * self.speed)
        
        if allow2: self.pos = nextPos
        else:
            #check for collision, get grid coords
            gX = math.floor(self.pos[0] // grid.tilesize)
            gY = math.floor(self.pos[1] // grid.tilesize)

            #get next pos grid cords
            ngX = math.floor(nextPos[0] // grid.tilesize)
            ngY = math.floor(nextPos[1] // grid.tilesize)

            #if next is equal to curr, move
            if (ngX, ngY) == (gX, gY):
                self.pos = nextPos

            else:
                #if next is inside grid
                if ngX >= 0 and ngX <= len(grid.grid) - 1 and ngY >= 0 and ngY <= len(grid.grid) - 1:
                    
                    #if tile is empty
                    if grid.grid[ngY][ngX] == 0:
                        #move
                        self.pos = nextPos
            
    def turn(self):
        #mouse turn
        pygame.mouse.set_visible(False)

        #get mouse x dif
        center = (screenWidth/2, screenHeight/2)

        xDif = pygame.mouse.get_pos()[0] - center[0]

        #turn for dif
        self.angle += xDif * self.rotationSpeed

        #reset mouse pos to center
        pygame.mouse.set_pos(center)

    def castAndDisplay(self, grid):
        angleDif = self.fov / (self.numOfRays-1)

        #create draw queue of rects for display slivers
        drawQueueRects = []
        drawQueueColors = []

        for i in range(self.numOfRays):
            #get rleative angle
            relAngle = self.angle - self.fov + i*angleDif

            #get direction vector
            angleRad = math.radians(relAngle)
            rayDir = (math.cos(angleRad) - math.sin(angleRad), math.sin(angleRad) + math.cos(angleRad))

            rayFin = (rayDir[0] * self.rayLength, rayDir[1] * self.rayLength)

            #get all intersections array for eahc line to get closest
            intersections = []
            
            for rect in grid.rects:
                clipped = rect.clipline((self.pos), (self.pos[0] + rayFin[0], self.pos[1] + rayFin[1]))
                for clip in clipped:
                    intersections.append(clip)

            #get closest intersection
            if len(intersections) >= 1:
                closest = intersections[0]
                closestMagSqrd = (closest[0] - self.pos[0])**2 + (closest[1] - self.pos[1])**2
                for inter in intersections:
                    #get len
                    vDif = (inter[0] - self.pos[0], inter[1] - self.pos[1])
                    vMagSqrd = vDif[0]**2 + vDif[1]**2
                    if closestMagSqrd > vMagSqrd:
                        closest = inter
                        closestMagSqrd = vMagSqrd

                #create display sliver and add it to draw queue
                closestMag = math.sqrt(closestMagSqrd)

                #get color
                ratio = closestMag/self.rayLength
                if ratio > 1: ratio = 1
                grayColor = 255 - 255 * ratio

                #set toon shader style
                if debug2: grayColor = grayColor//32 * 32

                newColor = (grayColor, grayColor, grayColor)
                drawQueueColors.append(newColor)

                #get rect
                newRect = pygame.Rect(
                    i * self.raysWidth,
                    (screenHeight / 2) - ((self.verticalFov / (closestMag + 0.00001)) / 2),
                    self.raysWidth,
                    self.verticalFov / (closestMag + 0.00001)
                )
                drawQueueRects.append(newRect)

        #draw to viewport
        #draw queued rays
        for i in range(len(drawQueueRects)):
            color = drawQueueColors[i]
            color = (color[0] % 255, color[1] % 255, color[2] % 255)
            pygame.draw.rect(screen, color, drawQueueRects[i])

#------------------------------------------------------------------------------------------------------------
def grainSurface(width, height, alpha, scale_factor):
    #create surface pixels array array
    lowResWidth = width // scale_factor
    lowResHeight = height // scale_factor

    surface = pygame.Surface((lowResWidth, lowResHeight))
    array = pygame.surfarray.pixels3d(surface)      #in format of array filled with r, g and b values seperate

    #fill with random values
    randm = np.random.randint(0, 255 + 1, (lowResWidth, lowResHeight), dtype=np.uint8)

    array[:, :, 0] = randm  #r
    array[:, :, 1] = randm  #g
    array[:, :, 2] = randm  #b

    del array

    #convert to alpha and apply transsparency
    surface = surface.convert_alpha()
    surface.set_alpha(alpha)

    #scale
    surface = pygame.transform.scale(surface, (width, height))

    return surface

#-----------------------------------------------------------------------------------------------------------------------------------------

#init objects

grid = Grid()
player = Player((45, 45))

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#get delta time initial ticks
prevT = pygame.time.get_ticks()

running = True
while running:

    #update delta time
    currT = pygame.time.get_ticks()
    dTms = currT - prevT
    dTs = dTms / 1000.0

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_LSHIFT:
                if allow1: player.speed = player.sprintSpeed
        
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT:
                player.speed = player.walkSpeed
    
    keys = pygame.key.get_pressed()

    #move
    if keys[pygame.K_w]:
        player.move(dTs, (1, 0), grid)
    if keys[pygame.K_a]:
        player.move(dTs, (0, -0.7), grid)
    if keys[pygame.K_s]:
        player.move(dTs, (-0.5, 0), grid)
    if keys[pygame.K_d]:  
        player.move(dTs, (0, 0.7), grid)

    #turn
    player.turn()

    # Fill screen
    screen.fill((0, 0, 0))

    #cast rays
    player.castAndDisplay(grid)

    #create grain overlay
    grain = grainSurface(screenWidth, screenHeight, 25, 4)
    if debug3: screen.blit(grain, (0, 0))

    # Update the display (buffer flip)
    if debug1: displayFPS(screen)
    pygame.display.flip()
    clock.tick(60)

    #update delta time
    prevT = currT

# Quit Pygame
pygame.quit()
