# Weekend-Sky
A dodge-em-up game I made to learn Python.
import pygame, sys
from pygame.locals import *
from math import *
from random import random, randint

import cProfile

pygame.init()

pygame.font.init()
gameFont = pygame.font.Font(None, 24)

FPS = 30
clock = pygame.time.Clock()

global screen
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 800
BORDER = 20
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
TOP, LEFT, BOTTOM, RIGHT = BORDER, BORDER, SCREEN_HEIGHT - BORDER, 500+BORDER
MID = (LEFT+RIGHT)/2
WIDTH = RIGHT - LEFT
HEIGHT = BOTTOM - TOP
SCREEN_RECT = Rect(LEFT, TOP, WIDTH, HEIGHT)

global gamestates
gamestates = ["title"]

#---Layer: background
global background
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((90, 0, 170))

#---Title of the game
pygame.display.set_caption('Hello')

'''Images'''

ImageDictionary = {}
ImageSizes = {}

def loadImg(filename, name, pixel=(0,0)):
    img = pygame.image.load('images/'+filename)
    img.convert()
    if pixel:
        img.set_colorkey(img.get_at(pixel))
    ImageDictionary[name] = img
    ImageSizes[name] = img.get_size()
    return img

def display(img, x, y, angle=0, onScreen=True):
    if angle != 0:
        rotatedID = img+"rotate"+str(angle)
        ImageDictionary[rotatedID] = rotate(ImageDictionary[img], angle)
        display(rotatedID, x, y)
        return
    if type(img) == str:
        imageID, img = img, ImageDictionary[img]
    (width, height) = img.get_size()
    x0 = x - width/2
    y0 = y - height/2
    img_rect = Rect(x0, y0, width, height)
    if onScreen:
        visibleArea = img_rect.clip(SCREEN_RECT).move(-x0, -y0)
        img_rect[0] += visibleArea[0]
        img_rect[1] += visibleArea[1]
    else:
        visibleArea = (0, 0, 100000000, 100000000) #max_int i.e. everything
    if not appleRectangles:
        screen.blit(img, img_rect, visibleArea)
    else:
        objectRects.append({"image":imageID, "rect":img_rect})

def displaytext(string, x, y, color=(0, 30, 170), size=24):
    thisFont = pygame.font.Font(None, size)
    textImg = thisFont.render(string, True, color)
    display(textImg, x, y, onScreen=False)

def faisceau(color, alpha):
    "Draws a foreground alpha rectangle over the frame."
    facade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    facade.fill(color)
    facade.set_alpha(alpha)
    screen.blit(facade, (0,0))

fading = False
fadeSpeed = 0
fadeColor = (0,0,0)
    

#---Images
bulletSizes = {}
catImg = loadImg('cat.png', 'cat')
playerImg = loadImg('player.png', 'player')
playerHit = loadImg('player hit.png', 'player hit')
blue01 = loadImg('blue01.png', 'blue01')
blue02 = loadImg('blue02.png', 'blue02')
blue03 = loadImg('blue03.png', 'blue03')
red01 = loadImg('red01.png', 'red01')
red02 = loadImg('red02.png', 'red02')
yellow03 = loadImg('yellow03.png', 'yellow03')
bulletSizes['red01'] = 7
bulletSizes['red02'] = 14
bulletSizes['blue01'] = 7
bulletSizes['blue02'] = 14
bulletSizes['blue03'] = 10
bulletSizes['yellow03'] = 8
fairyImg = loadImg('fairy.png', 'fairy01')
mysteryBox = loadImg('mystery box.png', 'box')
littleBox = loadImg('littlebox.png', 'littlebox')
warning = loadImg('warning.png', 'warning')
bulletSizes['warning'] = -1
sky = loadImg('sky.png', 'sky', None)
leaves = loadImg('leaves.png', 'leaves', None)
bulletSizes['box'] = 20
bulletSizes['littlebox'] = -1

title = loadImg('title.png', 'title')
splash = loadImg('splash.png', 'splash')
instructions = loadImg('instructions.png', 'instructions') # Also, this
arrow = loadImg('arrow.png', 'arrow')

endingBad = loadImg('endingGreat.png', 'endingBad')
endingOkay = loadImg('endingGreat.png', 'endingOkay')
endingGood = loadImg('endingGreat.png', 'endingGood')
endingGreat = loadImg('endingGreat.png', 'endingGreat')
endingPerfect = loadImg('endingGreat.png', 'endingPerfect')
# TODO: Draw the other endings.


#---Initialize bullets
global bullets
bullets = []


screen.blit(background, (0, 0))
pygame.display.update()

def shoot(image, **args):
    bullet = Bullet(image, **args)
    reference = ref(bullet)
    bullets.append(bullet)
    return reference

def queue(dictionary, key, value):
    '''Adds the value to the list dictionary[key].
    Useful for queueing events and bullets into the event queues.'''
    key = int(key) # Because now, times can be non-integral
    if dictionary.get(key):
        dictionary[key].append(value)
    else:
        dictionary[key] = [value]

def distance(x1, y1, x2, y2):
    return ((x1-x2)**2 + (y1-y2)**2)**0.5

def rotate(image, angle):
    newImage = pygame.transform.rotate(image, angle*180/pi)
    newImage.set_colorkey(image.get_colorkey())
    return newImage


def drawUI():
    display('leaves', SCREEN_WIDTH/2, SCREEN_HEIGHT/2, onScreen=False)

def drawScore():
    scoreRect = Rect(RIGHT+80, 120, 160, 60)
    screen.blit(leaves, scoreRect, scoreRect)
    displaytext("Boxes: "+str(boxes), RIGHT+150, 150, size=30)


def drawAttackPower(attackPower):
    attackRect = Rect(RIGHT+100, 380, 100, 130)
    screen.blit(leaves, attackRect, attackRect)
    displaytext("Attack Power:", RIGHT+150, 400, size=24)
    displaytext(str(attackPower), RIGHT+150, 450+5*attackPower,
                size=24+10*attackPower,
                color=[(0,70,255), (10,200,200), (0,255,0), (100,100,0),
                       (255,100,0), (255,10,10)][attackPower])


def rrange(start, step, num):
    result = []
    for i in xrange(num):
        result.append(start)
        start += step
    return result

def nextEvent():
    event += 1
    eventTime = 0

def bulletClear():
    for bullet in bullets:
        bullet.angle = atan2(bullet.y-playery, bullet.x-playerx)
        bullet.speed = 4
        bullet.accel = 1

def homing(self): # Meant to be used as an fb
    speed = self.__dict__.get('speed', 4)
    angle = atan2(playery - self.y, playerx - self.x)
    self.x += speed*cos(angle)
    self.y += speed*sin(angle)
        

def collidedWith(x, y, bullet, distance=None):
    if not distance: distance = bullet.radius
    bx, by = bullet.x, bullet.y
    if y - by > distance or by - y > distance: return False
    if x - bx > distance or bx - x > distance: return False
    return (bx-x)**2 + (by-y)**2 < distance**2


class Bullet:
    def __init__(self, image, **args):
        self.image = image
        self.rotatable = (self.image in ['yellow03', 'warning'])
        # Whether or not to rotate the image
        
        self.initTime = time
        (self.width, self.height) = ImageSizes[image]
        for arg in args:
            self.__dict__[arg] = args[arg]
        if not self.__dict__.get('createDelay'):
            self.createDelay = 0
        if not self.__dict__.get('createTime'):
            self.createTime = self.initTime + self.createDelay
        if not self.__dict__.get('radius'):
            self.radius = bulletSizes[self.image]
        if self.__dict__.get('fr'):
            self.startx, self.starty = self.x, self.y
        if not self.__dict__.get('buffer'):
            self.buffer = 0
            # How far outside the image the bullet can get without being deleted
            
        
    def position(self):
        return (self.x, self.y)
    
    def isOffscreen(self):
        if self.__dict__.get('killTime'):
            return (time - self.createTime) > self.killTime
        else:
            return ((self.x + self.width < LEFT - self.buffer) or
                    (self.x - self.width > RIGHT + self.buffer) or
                    (self.y + self.height < TOP - self.buffer) or
                    (self.y - self.height > BOTTOM + self.buffer))
                

    def update(self, deltaT=1):
        if self.__dict__.get('vx') != None:
            self.x += self.vx*deltaT
            self.y += self.vy*deltaT
            if self.__dict__.get('ax') != None:
                self.vx += self.ax*deltaT
                self.vy += self.ay*deltaT
            elif self.__dict__.get('accel'):
                direction = atan2(self.vy, self.vx)
                self.vx += self.accel*cos(direction)*deltaT
                self.vy += self.accel*sin(direction)*deltaT
        elif self.__dict__.get('angle') != None:
            self.x += self.speed*cos(self.angle)*deltaT
            self.y += self.speed*sin(self.angle)*deltaT
            if self.__dict__.get('accel'):
                self.speed += self.accel*deltaT
            if self.__dict__.get('angleaccel'):
                self.angle += self.angleaccel*deltaT
        elif self.__dict__.get('fr'): # relative to creation time, place
            relativePlace = self.fr(time - self.createTime)
            self.x, self.y = (relativePlace[0] + self.startx,
                              relativePlace[1] + self.starty)
        elif self.__dict__.get('fa'): # absolute to eventTime, grid
            self.x, self.y = self.fa(eventTime)
        elif self.__dict__.get('fb'): # function for complex movement
            self.fb(self)
            

    def display(self):
        if self.rotatable:
            display(self.image, self.x, self.y, -self.__dict__.get('angle',0))
        else:
            display(self.image, self.x, self.y)

    def rect(self):
        return (self.x - self.width/2, self.y - self.height/2,
                self.width, self.height)


'''----------------------------------------------------
                    CLASS BULLET, CLASS FAIRY
   ----------------------------------------------------'''



class Fairy:
    def __init__(self, image, **args):
        self.attacking = False # Whether the player should gain box points now
        self.image = image
        self.createTime = time
        self.boxes = defaultDifficulty
        self.numericalBoxes = self.boxes
        (self.width, self.height) = ImageSizes[image]
        for arg in args:
            self.__dict__[arg] = args[arg]
        if not self.__dict__.get("fire"):
            self.fire = lambda *args:False

        # Parsing the interpolation instructions!
        # First, handling the case where the first/last instructions are just
        # "top", "bottom", "left", or "right":
        # this is messy :(
        if self.interpolator[0] == "top":
            self.interpolator[0] = (0, self.interpolator[1][1],
                                    TOP-self.height)
        elif self.interpolator[0] == "bottom":
            self.interpolator[0] = (0, self.interpolator[1][1],
                                    BOTTOM+self.height)
        elif self.interpolator[0] == "left":
            self.interpolator[0] = (0, LEFT-self.width, self.interpolator[1][2])
        elif self.interpolator[0] == "right":
            self.interpolator[0] = (0, RIGHT+self.width,
                                    self.interpolator[1][2])
        if self.interpolator[-1][1] == "top":
            self.interpolator[-1] = (self.interpolator[-1][0],
                                     self.interpolator[-2][1],
                                     TOP-self.height)
        elif self.interpolator[-1][1] == "bottom":
            self.interpolator[-1] = (self.interpolator[-1][0],
                                     self.interpolator[-2][1],
                                     BOTTOM+self.height)
        elif self.interpolator[-1][1] == "left":
            self.interpolator[-1][1] = (self.interpolator[-1][0],
                                    LEFT-self.width,
                                    self.interpolator[-2][2])
        elif self.interpolator[-1][1] == "right":
            self.interpolator[-1] = (self.interpolator[-1][0],
                                    RIGHT+self.width,
                                    self.interpolator[-2][2])
        self.x = self.interpolator[0][1]
        self.y = self.interpolator[0][2]
        self.currentInstruction = 0
            
        
    def position(self):
        return (self.x, self.y)

    def shoot(self, image, **args):
        return shoot(image, **dict({"x":self.x, "y":self.y}, **args))

    def giveBox(self):
        self.boxes += 1
        self.numericalBoxes += 1
        # Maybe some 'mp3.wow' effect here, or a graphical effect

    def dropBoxes(self):
        number = int(self.numericalBoxes)
        self.numericalBoxes = 0
        for i in xrange(number):
            mysteryBoxes.append(Bullet('box', x=self.x + 50*cos(i),
                                       y=self.y + 50*sin(i),
                                        fb = homing, speed = 10))
        self.boxes = 0
                
    def update(self):
        lastpos = self.interpolator[self.currentInstruction]
        nextpos = self.interpolator[self.currentInstruction+1]
        selfTime = time - self.createTime
        fraction1 = float(selfTime - lastpos[0])/(nextpos[0] - lastpos[0])
        fraction2 = 1 - fraction1
        self.x = lastpos[1]*fraction2 + nextpos[1]*fraction1
        self.y = lastpos[2]*fraction2 + nextpos[2]*fraction1
        if selfTime >= nextpos[0]:
            self.currentInstruction += 1
            if self.currentInstruction >= len(self.interpolator)-1:
                return False # The call for this function will remove the fairy
        if self.attacking:
            self.numericalBoxes += [2, 3, 4, 5, 6, 8][self.boxes]*deltaT/120
            # The score/risk distribution can be changed later!
        for frame in eventTimes:
            self.fire(self, frame)
            

    def display(self):
        display(self.image, self.x, self.y)

    def rect(self):
        return (self.x - self.width/2, self.y - self.height/2,
                self.width, self.height)


class MysteryBox(Bullet):
    # I'm not sure if I actually need more class functionality for mystery boxes
    pass

class Particle(Bullet):
    # Also, not sure if I actually need more class functionality for particles
    pass



import weakref
from weakref import *
'''This module is very important for storing references to bullets!
Because of the way we handle bullet[]-type arrays, we can't just call
bullet[i], since the objects will be constantly shuffled around in the array.

So when we want to create a bullet and then alter its speed to, say, 17,
exactly 60 frames later, we can code something like this:

b = Bullet(image, args, &c.&c.)
r = ref(b)
bullets.append(b)
bulletChangeQueue(r, time+60, {vx:17})
(or whatever the bulletChangeQueue will be called)

Of course, this will all be wrapped up in a shoot() function.

In the current implementation, this is:

def setSpeedTo(bullet, value):
    bullet.speed = value           this may cause some common global functions

b = shoot(image, args, &c.&c.)
queue(bulletChangeQueue, time+60, (bullet, lambda b: setSpeedTo(b, 17)))

Of course, this can always be implemented with fr's or fa's instead.
'''


bullets = []
fairies = []
mysteryBoxes = []
boxes = 0
particles = []

speed = 4
speedFocus = 2

relativeY = 0 # For the "Preparing: ..." events

attackPower = 0

playerx = (LEFT+RIGHT)/2
playery = HEIGHT*2/3

defaultDifficulty = 0
useMysteryBox = 0

catx = (LEFT+RIGHT)/2
caty = HEIGHT*1/3

time = 0
frames = 0
eventID = "StarT"
eventTime = 0
deltaT = 0

invincibility = 0

eventQueue = {}
bulletChangeQueue = {}

keys = {K_RIGHT:False, K_LEFT:False, K_DOWN:False, K_UP:False, K_LSHIFT:False,
        K_RSHIFT:False, K_SPACE:False}

backgroundRects = []
appleRectangles = False # Sometimes, it's slower to use apple-picking rectangles

#---Aaaaaand start!

#game loop:
while True:
    if gamestates[-1] == "running":
        frames += 1
        clock.tick(60)
        
        if frames % 60 == 0:
            print "fps    ", clock.get_fps()
            print "time   ", clock.get_time()

        if frames == 1:
            drawUI()
            clock.tick()
            eventID = "StarT"

        deltaT = clock.get_time()*60/1000.0
        times = xrange(int(time)+1, int(time+deltaT)+1)
        time += deltaT
        eventTimes = xrange(int(eventTime)+1, int(eventTime+deltaT)+1)
        eventTime += deltaT

        if frames == 1:
            print deltaT, eventTime, time

        if not appleRectangles:
            display(sky, MID, (TOP+BOTTOM)/2)
        else:
            objectRects = []

        #---Danmaku!

        if eventID == "StarT":
          for frame in eventTimes:
            if frame == 1:

                directedAngle = 0
                directedAngle2 = 0

                def straightfire(self, frame):
                    if frame % 60 == 0 and frame > 100:
                        self.shoot('blue01', angle = directedAngle, speed = 3)
                        self.shoot('blue01', angle = directedAngle+pi, speed=3)
                    if frame % 60 in [31, 34] and self.boxes > 0:
                        self.shoot('red01', angle = directedAngle2, speed = 3)
                        self.shoot('red01', angle = directedAngle2+pi, speed=3)

                for pos in rrange(60, 85, 6):
                    fairies.append(Fairy('fairy01', interpolator = ["top",
                                        (50, pos, 100), (60*21, pos, 100),
                                        (60*21+150, "top")],
                                         fire = straightfire, attacking = True))

            if frame % 20 == 0:
                directedAngle = (random()-0.5)*pi/2 + pi/2
                directedAngle2 = (random()-0.5)*pi/2 + pi/2

            if frame == 60*9:
                thePlayerHasUsedABox = False
                mysteryBoxes.append(Bullet('box', x = MID, y = -20, fb=homing,
                                           killTime = 1000000, speed=10))

            if 60*18 > frame > 60*11 and not thePlayerHasUsedABox:
                boxes = 1 # If the player dies, messing with our scripted event
                displaytext("It's a mysterious treasure box!", MID,
                            200, size = 50)
                displaytext("Press Space to show the fairies what's inside.",
                            MID, 250, size = 24)
                if boxUsed:
                    thePlayerHasUsedABox = True
                    boxes = 0
                

            if frame == 60*18:
                for fairy in fairies:
                    fairy.fire = lambda *args: None

            if 60*23 > frame > 60*19:
                displaytext("Sharing these boxes is dangerous,",
                            MID, 200, size=30)
                displaytext("but it can be pretty rewarding!",
                            MID, 250, size=30)

            if frame == 60*21:
                for fairy in fairies:
                    fairy.numericalBoxes /= 10
                    fairy.numericalBoxes += 1 # In case it's 0
                    fairy.dropBoxes()

            if frame > 60*24:
                displaytext("Using these boxes makes fairies more and",
                            MID, 100, size=30)
                displaytext("more excited, up to a maximum level of 5.",
                            MID, 150, size=30)

            if frame > 60*26:
                displaytext("Be careful in balancing risk and reward,",
                            MID, 250, size=30)
                displaytext("and collect as many treasure boxes as you can!",
                            MID, 300, size=30)

            if frame > 60*30:
                eventTime = 0
                eventID = "Meandering Leaves"

        

        elif eventID == "Meandering Leaves":
          for frame in eventTimes: 
            if frame == 1:
                bulletChangeQueue = {}
                eventStartTime = time
                
                def setAccelTo(bullet, value):
                    bullet.accel = value # An obvious surrogate function.

                def fairyfire(self, frame):
                    if frame % (11-2*self.boxes) == 0:
                        bullet = self.shoot('yellow03',
                            angle = random()*2*pi, speed = 5, accel = -0.1)
                        queue(bulletChangeQueue, time+50,
                            (bullet, lambda bullet: setAccelTo(bullet, 0)))
                        queue(bulletChangeQueue,
                            (time-eventStartTime)/200*200+200+eventStartTime,
                            (bullet, lambda bullet: setAccelTo(bullet, 0.05)))

                leftOne = Fairy('fairy01', interpolator = ["top",
                                (60, (3*LEFT+RIGHT)/4, 200),
                                (600, (3*LEFT+RIGHT)/4, 200), (720, "top")],
                               fire = fairyfire, attacking = True)
                rightOne = Fairy('fairy01', interpolator = ["top",
                                (60, (LEFT+3*RIGHT)/4, 200),
                                (600, (LEFT+3*RIGHT)/4, 200), (720, "top")],
                               fire = fairyfire, attacking = True)
                fairies.append(leftOne)
                fairies.append(rightOne)


            if frame % 30 == 0 and eventTime < 60*8:
                spawnx = random()*(RIGHT-LEFT)+LEFT
                spawny = TOP
                mysteryBoxes.append(Bullet('box', x=spawnx, y=spawny,
                                               vx=0, vy=1.0, ax=0, ay=0.05))

            if eventTime > 60*6:
                (leftOne.fire, rightOne.fire) = (lambda *args: None,
                                                 lambda *args: None)

            if eventTime > 60*10:
                for fairy in fairies:
                    fairy.dropBoxes()

            if eventTime > 60*11:
                cat = Fairy('cat',
                            interpolator = ["top", (120, MID, 200),
                            (100000, MID, 200)])
                fairies.append(cat)
                eventID = "Preparing: Whirlwind: Localized Cyclone"
                eventTime = 0

        elif eventID == "Whirlwind: Localized Cyclone":
          for frame in eventTimes:
            if frame == 1:
                def catfire(self, frame):
                    if frame > 120 and frame % 4 == 0:
                        angle = frame**2/2500.0
                        bulletspeed = 4
                        n = 4+2*self.boxes
                        if self.boxes == 5: n = 20
                        for i in rrange(angle, 2*pi/n, n):
                            self.shoot('blue01', angle = i, speed = bulletspeed)

                cat.fire = catfire
                cat.attacking = True

            if eventTime > 60*10:
                cat.fire = lambda *args: None
                cat.attacking = False

            if eventTime > 60*11:
                cat.dropBoxes()
                cat.attacking = False
                eventID = "Preparing: High-Level Storm: High-Speed Revolution"
                eventTime = 0

        elif eventID.startswith("Preparing: "):
            # This is quite non-general, but we can specialcase out
            # the cases when it might not work.
            # It's handy to have a non-general case here!!!
            
            for frame in eventTimes:
                if frame == 1:
                    preparedEvent = eventID[11:] # Snips the "Preparing: " off
                    timeToNextEvent = frame+3*60

                    texts = ["Warning!",
                             preparedEvent,
                             "Use your mystery boxes!"]
                    textsSoFar = ["", "", ""]

            for i in xrange(len(texts)):
                if textsSoFar[i] != texts[i]:
                    textsSoFar[i] += texts[i][len(textsSoFar[i])]

            displaytext(textsSoFar[0], MID, 60+relativeY, size=60)
            displaytext(textsSoFar[1], MID, 100+relativeY, size=30)
            displaytext(textsSoFar[2], MID, 140+relativeY,
                        color=(255, 0, 0), size=20)
            if boxUsed:
                timeToNextEvent = eventTime+1*60 # Give time to use more boxes
            if eventTime > timeToNextEvent:
                eventID = preparedEvent
                eventTime = 0

        elif eventID == "High-Level Storm: High-Speed Revolution":
          for frame in eventTimes:
            if frame == 1:

                cat.createTime = time # just for the interpolator
                cat.currentInstruction = 0
                cat.interpolator = [(0, cat.x, cat.y), (200, MID, -50),
                                    (500*3, MID, -50), (500*3+60, cat.x, cat.y),
                                    (10000000, cat.x, cat.y)]

                cat.attacking = True

                def startRotating(rotationTime, startX, startY, c, reps):
                    distance = ((c[0]-startX)**2 + (c[1]-startY)**2)**0.5
                    startangle = atan2(startY-c[1], startX-c[0])
                    relcenter = (c[0]-startX, c[1]-startY)
                    speed = [0, 7000000, 5000000, 3000000][reps]
                    speed *= [1, 0.9, 0.8, 0.7, 0.6, 0.5][cat.boxes]
                    return lambda time: rotationFn(time-rotationTime,
                                        startangle, relcenter, distance, speed)

                def rotationFn(reltime, startangle, relcenter, distance, speed):
                    if reltime < 0:
                        angle = startangle # Hasn't started rotating yet
                    else:
                        angle = startangle + reltime**3/speed
                    return (relcenter[0]+cos(angle)*distance,
                            relcenter[1]+sin(angle)*distance)

                reps = 0


            if frame % 500 == 50 and reps < 3:
                reps += 1
                gridFineness = 140 - 20*cat.boxes
                xBullets = WIDTH/gridFineness
                yBullets = HEIGHT/gridFineness
                center = (randint(1, xBullets-1)*gridFineness+10,
                          randint(1, yBullets-1)*gridFineness+10)
                for x in xrange(xBullets+10):
                    for y in xrange(yBullets+10):
                        xpos = 10+(x-5)*gridFineness
                        ypos = 10+(y-5)*gridFineness
                        queue(eventQueue, time+(x+y),
                              Bullet('warning', x=xpos, y=ypos, angle=0,
                                     speed=0, angleaccel=0.1, killTime = 110))
                        # TODO: function "create warning" out
                        temp = Bullet('blue03', x=xpos, y=ypos,
                                    fr=startRotating(30, xpos, ypos,
                                    center, reps), killTime = 60*6+x)
                        queue(eventQueue, time+(x+y)+100, temp)

            if frame == 500*3+60:
                cat.dropBoxes()
                cat.attacking = False
                eventQueue = {}
                bulletChangeQueue = {}
                eventTime = 0
                eventID = "Preparing: Snake Storm: Raining Pythons"

        elif eventID == "Snake Storm: Raining Pythons":
          for frame in eventTimes:
            if frame == 1:

                cat.attacking = True
                
                def positionInAxes(x, y, angle):
                    return (x*cos(angle) + y*cos(angle+pi/2),
                            x*sin(angle) + y*sin(angle+pi/2))
                def createSquiggle(angle, speed):
                    return lambda cTime: positionInAxes(cTime*speed,
                                        sin(cTime*speed/30.0)*30*speed, angle)
                def homingfire(self, frame):
                    if frame % 100-10*self.boxes == self.randomFireTime:
                        self.shoot('red02', speed = 3,
                                   angle = atan2(playery - self.y,
                                                 playerx - self.x))

            bulletSpeed = 0.15 * (cat.boxes+10)
            if frame % (24 - 4*cat.boxes) == 0 and frame < 60*18:
                angle = random() + frame/12
                for i in rrange(0, 2+(cat.boxes)/5, 9+cat.boxes):
                    squiggler = Bullet('blue01', x = cat.x,
                        y = cat.y, fr = createSquiggle(angle, bulletSpeed),
                        killTime = ((WIDTH**2 + HEIGHT**2)**0.5)/bulletSpeed)
                    addTime = time + 3*i
                    queue(eventQueue, addTime, squiggler)

            if frame % 120-20*cat.boxes == 0 and frame < 60*20:
                fairies.append(Fairy('fairy01', interpolator = ["left",
                              (60, MID, 100), (120, "right")], fire=homingfire,
                               randomFireTime = int(random()*49),
                               boxes = cat.boxes))

            if frame > 60*20:
                eventQueue = {}
                cat.dropBoxes()

            if frame > 60*24:
                eventTime = 0
                eventID = "..."

                        
                        

        for realframe in times:
            for bullet in eventQueue.get(realframe, []):
                bullet.createTime = time # To synch time for fr
                bullets.append(bullet)

        for realframe in times:
            for instruction in bulletChangeQueue.get(realframe, []):
            # instruction will be [weakref to bullet, function to apply to it]
                if instruction[0](): # If the weak reference is still there
                    instruction[1](instruction[0]()) # Apply the function to it

                                          


        for frame in eventTimes:
          if frame % 60 == 0:
            print len(bullets)
        

        #---Move the player
        K_SHIFT = K_LSHIFT or K_RSHIFT
        speed_multiplier = (1 - 0.5*keys[K_SHIFT])
        playerx += (keys[K_RIGHT] - keys[K_LEFT])*speed*speed_multiplier*deltaT
        playery += (keys[K_DOWN] - keys[K_UP])*speed*speed_multiplier*deltaT
        edgeBuffer = 10
        if playerx < LEFT+edgeBuffer:
            playerx = LEFT+edgeBuffer
        elif playerx > RIGHT-edgeBuffer:
            playerx = RIGHT-edgeBuffer
        if playery < TOP+edgeBuffer:
            playery = TOP+edgeBuffer
        elif playery > BOTTOM-edgeBuffer:
            playery = BOTTOM-edgeBuffer
        if invincibility == 0 or (invincibility / 15) % 2 == 0:
            display('player', playerx, playery)
        else:
            display('player hit', playerx, playery)

            #---Use mystery boxes---

        boxUsed = False
        if useMysteryBox:
            if boxes > 0:
                for fairy in fairies:
                    if fairy.boxes < 5:
                        fairy.giveBox()
                        boxUsed = True
                if boxUsed:
                    boxes -= 1
                    particles.append(Bullet('littlebox', x=playerx, y=playery,
                                            vy=-5, vx=random(), ax=0, ay=0.2,
                                            killTime = 30))

        #---Move the bullets
        newbullets = []
        for bullet in bullets:
            bullet.update(deltaT)
            if not bullet.isOffscreen():
                newbullets.append(bullet)
            bullet.display()
        bullets = newbullets

        for box in mysteryBoxes:
            box.update(deltaT)
            if box.isOffscreen():
                mysteryBoxes.remove(box)
            box.display()

        for particle in particles:
            particle.update(deltaT)
            if particle.isOffscreen():
                particles.remove(particle)
            particle.display()

        #---Move the fairies
        for fairy in fairies:
            if fairy.update() == False:
                fairies.remove(fairy)
            fairy.display()
            

        #---Collision detection

        if not invincibility:
            for bullet in bullets:
                if collidedWith(playerx, playery, bullet):
                    # TODO: play sfx 'death', also 'fairies laughing'
                    invincibility = 60
                    bullets.remove(bullet)
                    bulletClear()
                    lostBoxes = min(10, boxes)
                    boxes -= lostBoxes
                    for fairy in fairies:
                        fairy.boxes = max(0, fairy.boxes - 1)
                        fairy.numericalBoxes /= 2
                    if lostBoxes != 0:
                        # Particle effects!
                        for angle in rrange(0, 2*pi/lostBoxes, lostBoxes):
                            particles.append(Bullet('littlebox', x=playerx,
                                    y=playery, angle=angle, speed=1, accel=0.5,
                                    killTime=30))
        else:
            invincibility -= 1

        for box in mysteryBoxes:
            if collidedWith(playerx, playery, box):
                boxes += 1 # Maybe add a "you collected a box" effect?
                # TODO: play sfx 'get box!'
                mysteryBoxes.remove(box)

        #---Finally...---

        if eventID == "...":
            faisceau((255, 255, 255), eventTime) # fade out
            if eventTime > 270:
                eventTime = 1
                gamestates[-1] = "ending"

        else:

            #---Display the score---
            drawScore()

            #---Display the attack power---
            prevAttackPower = attackPower
            attackPower = 0
            for fairy in fairies:
                if fairy.boxes > attackPower:
                    attackPower = fairy.boxes
            # Attack power = max over all fairies
            if attackPower != prevAttackPower:
                drawAttackPower(attackPower)



    #---Endings

    if gamestates[-1] == "ending":
        if eventTime == 1:
            gotoTitle = False
            # Choose the ending image
            if boxes < 50: endingImg = 'endingBad'
            elif boxes < 100: endingImg = 'endingOkay'
            elif boxes < 150: endingImg = 'endingGood'
            elif boxes < 200: endingImg = 'endingGreat'
            else: endingImg = 'endingPerfect'

        eventTime += 1
        display(endingImg, SCREEN_WIDTH/2, SCREEN_HEIGHT/2, onScreen=False)

        if eventTime < 255:
            faisceau((255, 255, 255), 255-eventTime) # fade in
            
        lightness = min(255, max(80, 400 - eventTime))
        displaytext("Total score: "+str(boxes), SCREEN_WIDTH/2,
                    BOTTOM-50, color=(lightness,lightness,255), size=60)

        displaytext("(Press Space to return to title)", SCREEN_WIDTH/2,
                    BOTTOM, color=(lightness,lightness,255), size=24)
        if keys[K_SPACE]:
            fading = True
            fadeSpeed = 2
            gotoTitle = True
        if gotoTitle and currentFade > 250:
            canChoose = False
            eventTime = 1
            gamestates[-1] = "splash"

    elif gamestates[-1] == "title":
        if eventTime == 0:
            fadeColor = (0,0,0)
            currentFade = 255
            fading = True
            fadeSpeed = -5
        eventTime += 1
        display('title', SCREEN_WIDTH/2, SCREEN_HEIGHT/2, onScreen=False)
        if eventTime == 50:
            fading = True
            fadeSpeed = 10
        if eventTime > 70:
            faisceau((0,0,0), 255)
        if eventTime > 80:
            eventTime = 1
            canChoose = False
            gamestates[-1] = "splash"

    elif gamestates[-1] == "splash":
        if eventTime == 1:
            selection = 0
            fading = True
            fadeSpeed = -4
            chosen = False # Whether the player has selected a menu item

        eventTime += 1
        display('splash', SCREEN_WIDTH/2, SCREEN_HEIGHT/2, onScreen=False)

        display('arrow', SCREEN_WIDTH/2 - 140 + selection*50,
                BOTTOM - 80 + selection*50, onScreen=False)


        if not chosen:

            if keys[K_UP]:
                selection = 0
            elif keys[K_DOWN]:
                selection = 1

            if keys[K_SPACE] and canChoose:
                chosen = True
                fading = True
                fadeSpeed = 10

            if not keys[K_SPACE]:
                canChoose = True
                

        else:
            if not fading:
                currentFade = 0
                eventTime = 0
                if selection == 0:
                    canGoBack = False
                faisceau((0,0,0), 255)
                gamestates[-1] = ["instructions", "running"][selection]

    elif gamestates[-1] == "instructions":
        display('instructions', SCREEN_WIDTH/2, SCREEN_HEIGHT/2, onScreen=False)
        if not keys[K_SPACE]:
            canGoBack = True
        elif canGoBack:
            faisceau((0,0,0), 255)
            canChoose = False
            eventTime = 1
            gamestates[-1] = "splash"
            
            
        #Process starting, etc



    #---Important Things

    if gamestates[-1] == "paused":
        clock.tick()

    useMysteryBox = 0 # Testing whether the player /just/ pressed Space

    #---For fade in, out---

    if fading:
        currentFade += fadeSpeed
        if currentFade < 0 or currentFade > 255:
            currentFade = min(255, max(currentFade, 0))
            fading = False
        faisceau(fadeColor, currentFade)

    #---Events---
        
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN
                                  and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == KEYUP or event.type == KEYDOWN:
            if event.type == KEYDOWN and event.key == K_p:
                if gamestates[-1] == "running":
                    gamestates.append("paused")
                else:
                    gamestates.pop()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                useMysteryBox = 1
            if event.type == KEYDOWN:
                keys[event.key] = True
            else:
                keys[event.key] = False
            
            

    '''pygame.display.update()'''
    
    #Apple-picking rectangles?

    # DEPRECATED - MAY NOT WORK ANYMORE

    if appleRectangles:
        updateRects = []
        
        for rect in backgroundRects:
            screen.blit(background, rect, rect)
            updateRects.append(rect)
        backgroundRects = []
        
        for drawing in objectRects:
            screen.blit(ImageDictionary[drawing['image']], drawing['rect'])
            updateRects.append(drawing['rect'])
            backgroundRects.append(drawing['rect'])
            
        pygame.display.update(updateRects)

    else:
        pygame.display.flip()


