import main

from graphics import *

win = GraphWin()
#CARS
def rendercar(car):
    p = car.parent
    if type(p) is Portal:
        # you would already know the x and y coordinates of the Portal
        pt = Point(portalX, portalY)
        cir = Circle(pt,3)
        cir.draw(win)
    if type(p) is Lane:
        # get the coordinates of the Lane
        pos = car.position
        pt = Point(laneX, laneY+pos)  # or pt == Point(pos+laneX,laneY), you have to figure this out
        cir = Circle(pt, 3)
        cir.draw(win)
    if type(p) is Middle:
        c1 = car.coords[0]
        c2 = car.coords[1]
        pt = Point(c1+middleX,c2+middleY)  # again, get coords of middle
        cir = Circle(pt, 3)
        cir.draw(win)

def render_Lane(lane): #DO NOT RENDER LANE, RENDER ROAD
    rectlane = Rectangle(Point(20,lane.length),pt)
    rect.draw(win)

#ROADS (DEPENDS ON LANES)
def render_Road(Road):

#Loops to check how many lanes there are to add that many lanes x units beside each other so there is no overlap
    for i in range(len(lane)):#len-lane is number of lanes
        rectroad = Rectangle(Point(20*i))

    road = Rectangle(Point()
    rect.draw(win)
    #How to draw for how many lanes there will be in the raod?

#PEDESTRIANS

def renderPedestrian(Pedestrian):

def renderIntersection(Intersection):
    render_Road()




def render_Middle(Middle):

def render_Zcrossing(ZebraCrossing):
