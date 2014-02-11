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


import time
import msvcrt  # windows-only :_(
from math import fmod
from threading import Timer


def get_bbox(asset):
    sp = asset.split("\n")
    return (max([len(_) for _ in sp]), len(sp))


def add_to_bufffer(screen, asset, x=0, y=0):
    x, y = int(x), int(y)
    h, w = get_bbox(asset)
    sp = asset.split("\n")
    for i, s in enumerate(sp):
        ln = screen[i + y]
        if x >= 0:
            ln = ln[:x] + s + ln[x + len(s):]
        else:
            ln = s[abs(x):] + ln[x + len(s):] + (" " * 80)
        screen[i + y] = ln
    screen = [l[:79] for l in screen]
    return screen[:26]


def key_pressed():
    global space
    if msvcrt.getch() == " ":
        space = True


def get_tube():
    gap = 6
    hmax = 22
    up = ("|     |\n" * (hmax - 2)) + ("-------\n" * 2)
    up = "\n".join(up.split("\n")[hmax - (hmax / 2 - gap):])
    dn = ("-------\n" * 2) + ("|     |\n" * (hmax - 2))
    dn = "\n".join((dn.split("\n")[:hmax / 2 - gap:]))
    return up, dn


def mainloop():
    global space, bird_vel, bird_pos, tubes, SCORE, tube_gap, TERMINAL_SIZE
    t = 0
    while True:
        # draw background
        b = BG.split("\n")
        b = add_to_bufffer(b, " SCORE: " + str(SCORE) + " ", 65, 24)
        b = add_to_bufffer(b, "Press <SPACE BAR>", 5, 24)

        # draw tubes
        minx = TERMINAL_SIZE[0]
        for i, tb in enumerate(tubes):
            posx = (TERMINAL_SIZE[0] + tb[1]) - t
            if fmod(i, 2) == 0:  # top tubes
                posy = 4
            else:
                posy = TERMINAL_SIZE[1] - tube_gap
            b = add_to_bufffer(b, tb[0], posx, posy)
            tubes[i][3] = (posx, posy)  # update position
            minx = posx if posx < minx else minx

        # draw bird
        # calc bird position
        f = [0, -2.5] if space else [0, 0]
        space = False
        for i in range(2):
            bird_vel[i] += GRAVITY[i]
            if i and bird_vel[i] > 1:
                bird_vel[i] = 1  # normalize velocity
            bird_vel[i] += f[i]
        bird_pos = [int(bird_pos[i] + bird_vel[i]) for i in range(2)]
        b = add_to_bufffer(b, BIRD, bird_pos[0], bird_pos[1])

        print "\n".join(b)

        # key event
        key_event = Timer(STEP, key_pressed)
        key_event.start()
        time.sleep(STEP)

        # check collisions:
        # background
        if any([bird_pos[1] + bird_bbox[1] > TERMINAL_SIZE[1] - 4,
                bird_pos[1] < 0]):
            return
        # tubes
        for tube in tubes:
            bx, by = tube[2]
            tx, ty = tube[3]
            condx = all([bird_pos[0] + bird_bbox[0] > tx,
                         bird_pos[0] < tx + bx])
            condy = all([bird_pos[1] + bird_bbox[1] > ty,
                         bird_pos[1] < ty + by])
            if condx and condy:
                return

        # update score
        if minx == 4:
            SCORE += 1

        # add tubes
        if fmod(t, 50) == 0:
            top, dwn = get_tube()
            tubes.append([top, t, get_bbox(top), (0, 0)])
            tubes.append([dwn, t, get_bbox(dwn), (0, 0)])
        tubes = [x for x in tubes if t - x[1] < 86]  # filter

        t += 1

if __name__ == "__main__":
    # config
    SCORE = 0
    STEP = 0.1
    GRAVITY = (0, 0.2)
    TERMINAL_SIZE = (80, 25)

    # assets
    BG = (" " * TERMINAL_SIZE[0] + "\n") * (TERMINAL_SIZE[1] - 3) + \
        ("=" * TERMINAL_SIZE[0] + "\n") + ("." * TERMINAL_SIZE[0] + "\n") * 3
    BIRD = " / (._\n===_/-"
    # BIRD = "/ O o\\\n\  V /"
    # game vars
    space = False
    tube_gap = 8
    bird_pos = [10, 0]
    bird_vel = [0, 0]
    bird_bbox = get_bbox(BIRD)
    tubes = list()

    # run
    mainloop()
    # game over
    print " " * TERMINAL_SIZE[0] * TERMINAL_SIZE[1]  # clear screen
    print "GAME OVER"
    print "SCORE:", str(SCORE)
