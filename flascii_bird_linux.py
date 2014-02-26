# This file is part of flascii_bird.
# Copyright (C) 2014 Cesar Saez

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import time, sched, sys, tty ,termios
##import msvcrt  # windows-only :_(
from math import fmod, sqrt
from threading import Timer
from random import randint
import select


class Vector(object):

    def __init__(self, x, y):
        super(Vector, self).__init__()
        self.x, self.y = x, y

    def __add__(self, vector):
        if isinstance(vector, self.__class__):
            return self.__class__(self.x + vector.x, self.y + vector.y)
        return super(Vector, self).__add__(vector)

    def __mul__(self, vector):
        if isinstance(vector, self.__class__):
            return self.__class__(self.x * vector.x, self.y * vector.y)
        return self.__class__(self.x * vector, self.y * vector)

    def __repr__(self):
        return "{0}, {1}".format(self.x, self.y)

    @property
    def length(self):
        return sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self):
        _length = self.length
        self.x = self.x / _length
        self.y = self.y / _length


class Sprite(object):

    def __init__(self, shape):
        self.shape = shape
        self.pos = Vector(0, 0)
        self.vel = Vector(0, 0)

    @property
    def bbox(self):
        if not hasattr(self, "_bbox"):
            sp = self.shape.split("\n")
            self._bbox = Vector(max([len(x) for x in sp]), len(sp))
        return self._bbox

    @property
    def shape(self):
        if type(self._shape) in (list, tuple):
            index = 0 if self.vel.y > 0 else 1
            return self._shape[index]
        return self._shape

    @shape.setter
    def shape(self, value):
        self._shape = value

    def simulate(self, forces=None, max_speed=2):
        forces = forces or list()
        for f in forces:
            self.vel = self.vel + f  # time, mass == 1
        if self.vel.length > max_speed:
            self.vel.normalize()
            self.vel = self.vel * max_speed
        self.pos = self.pos + self.vel

    def collide(self, obstacles=None):
        obstacles = obstacles or list()
        for o in obstacles:
            condx = all([self.pos.x + self.bbox.x > o.pos.x,
                         self.pos.x < o.pos.x + o.bbox.x])
            condy = all([self.pos.y + self.bbox.y > o.pos.y,
                         self.pos.y < o.pos.y + o.bbox.y])
            if condx and condy:
                return True
        return False

    def draw(self, BG):
        BG = BG.split("\n")
        self.pos.x, self.pos.y = int(self.pos.x), int(self.pos.y)  # rasterize
        for i, s in enumerate(self.shape.split("\n")):
            x = BG[i + self.pos.y]
            if self.pos.x >= 0:
                x = x[:self.pos.x] + s + x[self.pos.x + len(s):]
            else:
                x = s[abs(self.pos.x):] + x[self.pos.x + len(s):] + (" " * 79)
            BG[i + self.pos.y] = x
        return "\n".join([x[:79] for x in BG][:25])




def IsData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

def flascii_bird():
    global KEY_PRESSED
    SCORE = 0
    STEP = 0.1
    GRAVITY = Vector(0, 1)
    KEY_STRENGHT = Vector(0, -6)
    TERMINAL_SIZE = Vector(79, 25)

    BG = (" " * TERMINAL_SIZE.x + "\n") * TERMINAL_SIZE.y
    TUBES = list()
    GROUND = ("=" * TERMINAL_SIZE.x + "\n") + \
        ("." * TERMINAL_SIZE.x + "\n") * 3
    GROUND = Sprite(GROUND)
    GROUND.pos = Vector(0, 21)
    BIRD = Sprite(("== (.\n \___\\", " / (./\n===_/"))
    BIRD.pos = Vector(10, 0)

    t = 0

    while True:
        fd=sys.stdin.fileno()
        old_settings = termios.tcgetattr(sys.stdin)
        #tty.setraw(fd,termios.TCSANOW)
        tty.setcbreak(sys.stdin.fileno())
        t += 1
        time.sleep(STEP)
        if IsData():
            ch=sys.stdin.read(1)
            if ch==" ":
                KEY_PRESSED=True
        else:
            print "false"


        termios.tcsetattr(fd,termios.TCSADRAIN,old_settings)  ## if this setence in the game over,graph not right


        if fmod(t, 51) == 0 or t == 1:
            pipe_height = randint(1, 7)
            up = Sprite("|      |\n" * pipe_height + "--------\n--------")
            up.pos = Vector(TERMINAL_SIZE.x, 0)
            TUBES.append(up)
            dn = Sprite("--------\n" * 2 + "|      |\n" * (8 - pipe_height))
            dn.shape = dn.shape[:-1]  # remove last \n
            dn.pos = Vector(TERMINAL_SIZE.x,
                            TERMINAL_SIZE.y + pipe_height - 8 - 6)
            TUBES.append(dn)
            TUBES = [x for x in TUBES if x.pos.x > -7]  # cleanup
        f = Vector(-1, 0)
        for x in TUBES:
            x.simulate([f], max_speed=1)

        # bird
        BIRD.simulate([GRAVITY])
        if KEY_PRESSED:
            KEY_PRESSED = False
            BIRD.vel = KEY_STRENGHT
            BIRD.simulate(max_speed=25)  # dont clamp velocity

        # score
        for x in TUBES:
            if x.pos.x == BIRD.pos.x - 9:
                SCORE += 0.5  # each tube
        SCORE = int(SCORE)

        # draw
        frame = GROUND.draw(BG)
        for x in TUBES:
            frame = x.draw(frame)
        s = Sprite(" SCORE: " + str(SCORE) + " ")
        s.pos = Vector(60, 23)
        docs = Sprite(" PRESS <SPACEBAR> ")
        docs.pos = Vector(5, 23)
        for x in (s, docs):
            frame = x.draw(frame)
        print BIRD.draw(frame)

        # collisions
        colliders = list(TUBES)
        colliders.append(GROUND)
        if BIRD.collide(colliders) or BIRD.pos.y < 0:
            # game over
            print (" " * TERMINAL_SIZE.x + "\n") * TERMINAL_SIZE.y
            print "GAME OVER"
            print "SCORE:", SCORE
            return

if __name__ == "__main__":
    KEY_PRESSED = False
    flascii_bird()
