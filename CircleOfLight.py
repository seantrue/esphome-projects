import time
import random

NPIXELS=7 # LOLIN RGBLED
STARTPIXEL=1

#NPIXELS=24 #Ring
#STARTPIXEL=0

RATE=10
INTERVAL=1.0/RATE
MINBRIGHT=0
MAXBRIGHT=128

color = [128,0,0]
direction = [1,1,1]
display_mode = 1
write_over_color = False
over_color = [0,0,0]

def virtual_write_callback(value, pin, state):
    global color, direction, MINBRIGHT, MAXBRIGHT, display_mode, write_over_color
    v = value[0]
    if pin == 0:
        over_color[0] = int(v)
    elif pin == 1:
        over_color[1] = int(v)
    elif pin == 2:
        over_color[2]  = int(v)
        write_over_color = True
    elif pin == 3:
        # Should change direction
        direction[0] *= -1
        direction[1] *= -1
        direction[2] *= -1
    elif pin == 4:
        # Change speed
        pass
    elif pin == 5:
        MINBRIGHT=int(v)
    elif pin == 6:
        MAXBRIGHT=int(v)
    elif pin ==7:
        display_mode = int(v)

def new_color():
    global color
    for i in range(3):
        if write_over_color:
            color[i] = over_color[i]
        else:
            if urandom.getrandbits(10) > 900:
                direction[i] *= -1
            c = color[i]

            delta = urandom.getrandbits(4)
            c += (delta*direction[i])
            c = max(0,min(MAXBRIGHT,c))
            color[i] = c
            if c == MINBRIGHT or c == MAXBRIGHT:
                direction[i] *= -1

def Tfunc(st):
    global write_over_color
    if display_mode == 1:
        for j in range(STARTPIXEL,NPIXELS):
            np[j] = tuple(color)
            np.write()
            new_color()
    write_over_color = False
# Ticker is running at 200hz
b.Ticker(Tfunc,80)

print( "Mem: ", gc.mem_free())
b.run()



