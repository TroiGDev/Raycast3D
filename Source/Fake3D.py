import pygame
import random
import math

pygame.init()
screenWidth = 1200
screenHeight = 600
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('Fake3D')

#fps display
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 25)
def displayFPS(screen):
    fps = int(clock.get_fps())
    fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))  # White text
    screen.blit(fps_text, (10, 10))  # Top-left corner with slight padding

#debug toggle
debug1 = True
debug2 = False
debug3 = True

#-----------------------------------------------------------------------------------------------------------------------------------------

class Grid():
    def __init__(self):
        self.tilesize = 30

        #filled up with rects for acces in line intersection using pygames clipline
        self.rects = []

        self.grid = [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,1,1,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,1,0,0,0,0,0,1,1,1,0,0,1,1,1,1,1,0,0],
            [0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0],
            [0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,0,0],
            [0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0],
            [0,0,1,1,0,1,1,1,1,1,1,1,0,1,1,0,0,1,0,0],
            [0,0,0,1,0,0,0,1,0,0,0,1,0,0,1,1,1,1,0,0],
            [0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0],
            [0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0],
            [0,0,0,1,1,0,1,1,1,0,1,1,0,0,0,1,0,0,0,0],
            [0,0,0,1,0,0,0,1,0,0,0,1,1,0,1,1,0,0,0,0],
            [0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0],
            [0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        ]

        #initial draw grid
        self.drawGrid()

    def drawGrid(self):
        self.rects = []
        #draw grid lines
        if debug1:
            for y in range(len(self.grid) - 1):
                for x in range(len(self.grid[y]) - 1):
                    #draw grid line
                    pygame.draw.line(screen, (0, 0, 0), (self.tilesize * (x+1), 0), (self.tilesize * (x+1), screenHeight), 2)
                #draw grid line
                pygame.draw.line(screen, (0, 0, 0), (0, self.tilesize * (y+1)), (screenWidth/2 - 2, self.tilesize * (y+1)), 2)
        
        #draw  grid tiles
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
        self.numOfRays = 300
        self.raysWidth = screenWidth/self.numOfRays/2
        self.rayLength = 600

        self.speed = 50
        self.walkSpeed = 50
        self.sprintSpeed =self.walkSpeed * 2.5
        self.rotationSpeed = 0.15

        self.width = 10

    def draw(self):
        pygame.draw.circle(screen, (255, 255, 255), self.pos, self.width/2)

        #get angle line
        angleRad = math.radians(self.angle)
        v = (math.cos(angleRad), math.sin(angleRad))
        vMag = math.sqrt(v[0]**2 + v[1]**2)
        vNor = (v[0] / vMag, v[1] / vMag)
        vFin = (vNor[0] * 15, vNor[1] * 15)

        pygame.draw.line(screen, (255, 255, 255), self.pos, (self.pos[0] + vFin[0], self.pos[1] + vFin[1]), 3)

    def move(self, deltaTime, vDir):
        #rotate vDir by angle for ralative to player
        angleRad = math.radians(self.angle)
        xRot = vDir[0] * math.cos(angleRad) - vDir[1] * math.sin(angleRad)
        yRot = vDir[0] * math.sin(angleRad) + vDir[1] * math.cos(angleRad)
        vRel = (xRot, yRot)

        #apply movement vector * deltatime
        self.pos = (self.pos[0] + vRel[0] * deltaTime * self.speed, self.pos[1] + vRel[1] * deltaTime * self.speed)

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

    def CastRays(self, grid):
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

            #draw line
            if debug2: pygame.draw.line(screen, (255, 0, 0), self.pos, (self.pos[0] + rayFin[0], self.pos[1] + rayFin[1]), 1)

        #-----CLIPLINE COLLISION METHOD----------------------------------------------------------------------------------------------------------------------------------
            #get all intersections array for eahc line t get closest
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

                #after getting closest draw line to it
                if debug1: pygame.draw.line(screen, (120, 0, 0), self.pos, closest, 3)

                #create display sliver and add it to draw queue
                closestMag = math.sqrt(closestMagSqrd)

                #get color
                newColor = (255 - 255 * (closestMag/self.rayLength), 255 - 255 * (closestMag/self.rayLength), 255 - 255 * (closestMag/self.rayLength))
                drawQueueColors.append(newColor)

                #get rect
                newRect = pygame.Rect(
                    (screenWidth/2) + (i * self.raysWidth),
                    (screenHeight / 2) - ((self.verticalFov / (closestMag + 0.00001)) / 2),
                    self.raysWidth,
                    self.verticalFov / (closestMag + 0.00001)
                )
                drawQueueRects.append(newRect)

        #draw to viewport

        #draw different color ground and sky
        pygame.draw.rect(screen, (120, 120, 120), pygame.Rect(screenWidth/2, 0, screenWidth/2, screenHeight/2))
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(screenWidth/2, screenHeight/2, screenWidth/2, screenHeight/2))

        #draw queued rays
        for i in range(len(drawQueueRects)):
            color = drawQueueColors[i]
            color = (color[0] % 255, color[1] % 255, color[2] % 255)
            pygame.draw.rect(screen, color, drawQueueRects[i])
        
#-----------------------------------------------------------------------------------------------------------------------------------------

grid = Grid()
player = Player((30, 30))

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
                player.speed = player.sprintSpeed
        
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT:
                player.speed = player.walkSpeed
    
    keys = pygame.key.get_pressed()

    #move
    if keys[pygame.K_w]:
        player.move(dTs, (1, 0))
    if keys[pygame.K_a]:
        player.move(dTs, (0, -1))
    if keys[pygame.K_s]:
        player.move(dTs, (-1, 0))
    if keys[pygame.K_d]:  
        player.move(dTs, (0, 1))

    #turn
    player.turn()

    # Fill screen
    screen.fill((20, 20, 20))

    #draw tiles
    if debug3: grid.drawGrid()

    #draw player
    player.draw()

    #cast rays
    player.CastRays(grid)

    #draw crosshair
    pygame.draw.circle(screen, (255, 0, 0), (screenWidth / 2 + screenWidth/4, screenHeight / 2), 4, 2)

    # Update the display (buffer flip)
    displayFPS(screen)
    pygame.display.flip()
    clock.tick(60)

    #update delta time
    prevT = currT

# Quit Pygame
pygame.quit()
