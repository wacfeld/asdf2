import random

# TODO: Figure Out Numbers for stuff labeled FON

class Portal:  # called Portal because cars/pedestrians start and end here (there are multiple portals)
    # attaches to road of intersection
    # cars coming from the intersection go directly from Middle to Portal

    def __init__(self, road, pos):
        self.cars = []
        self.peds = []
        self.adjroad = road  # the road it feeds into'
        self.finished = []  # cars and peds who are done
        self.position = pos  # 0, 1, 2, 3 -> up, right, down, left, see MindController.decidedest()

    # TODO: should we merge cars and peds into one list (as well as the functions)?
    def createcar(self):
        newcar = Car(self)
        self.cars.append(newcar)
        return newcar  # gives car to MindController, the one that calls the function and decides the car's destination

    def createped(self):  # basically same as createcar()
        newped = Pedestrian(self)
        self.peds.append(newped)
        return newped

    def deleteobj(self, c):  # removes car forever
        del self.finished[self.finished.index(c)]  # get index of c in cars, then delete that element

    def releasesome(self):
        # takes at most 1 car and all pedestrians and pushes them into the adjacent road
        c = self.cars.pop(0)
        self.adjroad.giveroad(c)
        for p in peds:
            self.adjroad.giveroad(p)
        del peds[:]

    def deletefinished(self):
        for c in self.finished:
            deleteobj(c)

    def onetick(self):
        if random.random() < Portal.carprob:
            self.createcar()
        if random.random() < Portal.pedprob:
            self.createped()

        self.deletefinished()  # get rid of cars and peds who
        self.releasesome()

    carprob = 0.1  # (FON) probability that a car will spawn in a given tick, similar below
    pedprob = 0.03  # (FON)


class Car:
    def __init__(self, p):
        # cars spawn in Portals which are adjacent to the outer intersections
        # location == 'l', 'p' is digital; 'm' is analog
        # when turning cars follow a rough circle

        self.parent = p  # either Portal, Lane, or Middle; this also tells us how it should behave
        # ^cars are always in a digital state

        self.destination = None  # the portal it wants to get to

        # these only apply when in the middle of an intersection
        self.coords = [None, None]  # (0,0) is center of Intersection, x moves right, y moves up
        self.motionvector = [None, None]  # where it moves next in the Intersection; might change to direction and angle

        self.reacheddest = False  # TODO: obsolete?


class Lane:
    def __init__(self, d, parent, c):
        self.cars = []  # first in the array are closest to middle of intersection
        self.direction = d  # direction is l, r, or f
        self.parentroad = parent
        self.capacity = c  # (FON) how many cars it can hold; right and left are less, forward is more


class Road:
    # FON: number of lanes - 2 or 3?
    # note that intersections at the edge still have 4 roads (1 or 2 are technically Portals)

    def __init__(self, p):
        self.left = Lane('l', self, self.rc[0])
        self.forward = Lane('f', self, self.rc[1])
        self.right = Lane('r', self, self.rc[2])
        self.lanes = [self.left, self.forward, self.right]

        self.parent = p

        self.crossing = ZebraCrossing(self)  # placed here for easy access from cars
        self.light = Light(self)  # note that lights control the road they belong to, not the opposite!

        self.temp = []  # where pedestrians and cars go before being sorted and stuff by onetick()


    rc = [5,10,5]  # (FON) respective capacity; how much each lane can hold; should be random

    def giveroad(self, obj):  # gets a ped or car from adjacent portal or intersection
        self.temp.append(obj)

    def onetick(self):
        for t in temp:
            if type(t) is Car:  # then put it into a lane

class Middle:
    # the middle of the intersection; split up into nxn squares
    # n must be even to evenly split up the roads leading in and out
    # certain square are special; e.g. some are places a car can leave or enter an intersection

    def __init__(self, parent):
        self.squares = [[None] * self.middlesize for i in range(self.middlesize)]
        self.parent = parent

    middlesize = 6  # (FON) must be even number


class Sidewalk:
    # small square at the four corners of intersections, where pedestrians stay when not crossing roads
    def __init__(self, p, c1, c2):
        self.parent = p
        self.peds = []
        self.crossing1, self.crossing2 = c1, c2


class Pedestrian:
    # walking is a digital task
    # different pedestrians have different walking speeds
    # when a pedestrian walks it occupies, the crossing, stays on the same sidewalk,
    # then after x time goes to the other sidwalk and unoccupies the crossing

    def __init__(self, p):
        self.walkingspeed = Pedestrian.decidewalkingspeed()
        self.parent = p  # a Sidewalk
        self.reacheddest = False  # TODO: obsolete?
        self.iswalking = False

    @staticmethod
    def decidewalkingspeed():
        # TODO: figure this out, must be Gaussian random
        pass


class ZebraCrossing:
    # where pedestrians cross; pedestrians do not move, but take x time to cross
    # since by law you aren't allowed to drive if the pedestrians are anywhere on the pavement
    # belongs to Road object

    def __init__(self, parent):  # parent is a Road
        # when a pedestrian is crossing it adds 1 to numberofpedestrians, when it leaves it subtracts 1
        # the crossing checks when numberofpedestrians == 0 and then it becomes not occupied
        self.occupied = False
        self.numberofpedestrians = 0
        self.light = Light(self)

        self.parentroad = parent

        self.pedlight = Light(self)

    def checkoccupied(self):  # called by pedestrian before and after crossing
        return not bool(self.numberofpedestrians)


class Light:  # applies to traffic and pedestrian lights, since they are effectively the same, except in timing
    def __init__(self, parent):  # will figure out parenttype on its own
        self.state = 'r'
        self.parenttype = 'z' if type(parent) is ZebraCrossing else 'r'
        self.parent = parent

    # either 'z' for zebra crossing, or 'r' for road
    parenttype = None  # we can infer the light type from this
    parent = None  # either Road or ZebraCrossing
    state = None  # can be 'r', 'y', 'g','l', last one means left turning, doesn't apply for pedestrian lights


class Intersection:
    # an intersection consists of 4 roads and a middle; everything else is contained inside the roads
    # intersections do NOT have roads leading out of them, only in
    # once a car goes through, it immediately transfers to the next intersection

    # whichroads is a string of 4 1s and 0s telling you what roads are active, going clockwise
    # note that an inactive road is not necessarily an edge road, since the edges typically have roads for the portals
    # adj always is a tuple of 4 since if it's on the edge it has portals
    def __init__(self, gc):
        self.adjacents = [None] * 4  # intersections/portals adjacent to this intersection
        self.middle = Middle(self)

        self.gridcoords = gc  # used by MindController.pathfind() to figure out where it's located on the grid

        # initiates roads
        # roads are ordered clockwise, starting from top
        self.roads = []
        for i in range(4):  # b for boolean
            newroad = Road(self)
            self.roads.append(newroad)

        # set the crossings corresponding to sidewalks
        s1 = Sidewalk(self, self.roads[0], self.roads[1])
        s2 = Sidewalk(self, self.roads[1], self.roads[2])
        s3 = Sidewalk(self, self.roads[2], self.roads[3])
        s4 = Sidewalk(self, self.roads[3], self.roads[1])


class MindController:
    # this controls all the interactions of the simulation, aside from the traffic lights
    # does things like make cars move, spawn, etc.

    def __init__(self, s):
        self.sidelength = s  # not including Portals
        self.intersections = [[None] * s for i in range(s)]
        self.initinter(s)
        self.portals = []  # for easy access
        self.ticks = 0  # time for the simulation; 1 tick is 1/2 a "second"

    @staticmethod
    def decidedest(self, p):
        # takes portal and returns a portal which isn't on the same side
        ppos = p.position  # for convenience

        # aside from U-turns, cars never go back the same direction
        # and accuracy regarding destination choice shouldn't matter too much
        diffpos = lambda x: x.position != ppos
        allonothersides = list(filter(diffpos, self.portals))  # filter out portals on the same side as p
        dest = random.choice(allonothersides)

        return dest

    @staticmethod
    def pathfind(self, origin, dest):
        # we use the A* algorithm to simulate human pathfinding (with a map)
        # returns array of intersections to follow, and the portal (for conevnience and corner cases)
        closedset = []  # already evaluated intersections
        openset = [origin.adjroad.parent]  # currently discovered but not evaluated
        



    def initinter(self, s):
        for y in range(s):  # y goes top to bottom
            for x in range(s):  # x goes left to right
                self.intersections[y][x] = Intersection([x,y])

        # need to do this twice (^) to set the adjacent property
        for y in range(s):
            for x in range(s):
                inter = self.intersections[y][x]
                coords = [[x, y-1], [x+1, y], [x, y+1], [x-1, y]]

                for adjcoord in coords:
                    a = adjcoord[0]  # abbreviation
                    b = adjcoord[1]

                    if (not a in range(s)) or (not b in range(s)):  # then we create a portal
                        road = inter.roads[0] if a < y else inter.roads[1] if x < b else inter.roads[2] if y < a else inter.roads[3]

                        portalpos = coords.index([a, b])
                        portal = Portal(road, portalpos)
                        inter.adjacents[portalpos] = portal
                        self.portals.append(portal)
                    else:
                        inter.adjacents[coords.index([a, b])] = self.intersections[b][a]

    def onetick():  # does everything that happens in a single tick
        # (almost?) every has has a similar function which is called by this one
        # spawn and release cars, make everything move forwards, increments waiting counters, etc.
        for p in self.portals:
            p.onetick()

        for


def main():
    print('Program start')
    mc = MindController(3)  # (FON)


if __name__ == '__main__':
    main()