# Intersection, Road, Lane, Middle - big infrastructure stuff

import entities, virtual


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
            newroad = Road(self, i)
            self.roads.append(newroad)

        r1, r2, r3, r4 = self.roads[0], self.roads[1], self.roads[2], self.roads[3]  # for ease of use

        # set the crossings corresponding to sidewalks
        s1 = Sidewalk(self, r1.crossing, r2.crossing)
        s2 = Sidewalk(self, r2.crossing, r3.crossing)
        s3 = Sidewalk(self, r3.crossing, r4.crossing)
        s4 = Sidewalk(self, r4.crossing, r1.crossing)
        self.sidewalks = [s1, s2, s3, s4]

        # set the road's sidewalk attributes, for Intersection.gettargetsidewalk()
        r1.sw1, r1.sw2 = s4, s1
        r2.sw2, r2.sw2 = s1, s2
        r3.sw2, r3.sw2 = s2, s3
        r4.sw2, r4.sw2 = s3, s4

    @staticmethod
    def getrelativedirection(facing, ad):
        # facing is the orientation of the road
        # ad is the absolute direction the car should move
        mapping = {[0,2]:1, [1,3]:1, [2,0]:1, [0,3]:2, [1:0]:2, [2,1]:2, [3,2]:2, [0,1]:0, [1,2]:0, \
          [2,3]:0, [3,0]:0}  # left, forward, right = 0, 1, 2

        return mapping[[facing,ad]]

    @staticmethod
    def distfromnextcar(pos1, path1, point2):  # get distance in path of car 1 (in lane) to car 2 (in middle)
        # pos1 is position of car in lane
        # path1 is array of points which car in lane follows
        # point2 is location of car in middle
        pass

    def onetick(self):
        pass

    def getoppositeroad(self, r):
        pass


class Road:
    # FON: number of lanes - 2 or 3?
    # note that intersections at the edge still have 4 roads (0 or 1 or 2 are technically Portals)

    def __init__(self, p, ad):
        self.rc = self.getlens()  # respective capacities

        self.left = Lane(0, self, self.rc[0])
        self.forward = Lane(1, self, self.rc[1])
        self.right = Lane(2, self, self.rc[2])
        self.lanes = [self.left, self.forward, self.right]

        self.absolutedir = ad  # the way the road is facing based off the whole grid
        self.parent = p

        self.crossing = ZebraCrossing(self)  # placed here for easy access from cars
        self.sw1 = None  # initialized by Intersection after Sidewalks are made
        self.sw2 = None  # ordered RTL, facing Middle
        self.pedwaiting = []  # pedestrians wait before moving to sidewalk

        self.light = Light(self)  # note that lights control the road they belong to, not the opposite!

        self.speedlimit = None  # either 40, 50, or 60 km/h, or 11.11, 13.88, 16.66 m/s
        self.length = self.decidelength()  # meters

    @staticmethod
    def decidelength():
        pass

    @staticmethod
    def getlens():  # length in meters of all three lanes, random
        pass

    # TODO: make the car figure out the next Lane to go to while in the previous intersection
    def offerroad(self, obj):  # something tries to give road a ped or car from adjacent portal or intersection
        # if failed the Portal/Midle keeps it
        # named this way to avoid confusion - Road is being given object
        obj.parent = self
        if type(obj) is Car:
            if obj.lanetoenter == None:  # then figure that out, this is kept if the car is rejected
                currgc = self.parent.gridcoords
                nextgc = obj.path[1].gridcoords  # intersection after this one in Pedestrian's path
                del obj.path[0]
                absolutedirection = MindController.directiontotake(currgc, nextgc)  # up, right, down, left -> 0, 1, 2, 3
                reldir = Intersection.getrelativedirection(self.ad, absolutedirection)
                obj.lanetoenter = self.lanes[reldir]

            if obj.lanetoenter.carcanenter():
                # set the variables in Car
                obj.parent = obj.lanetoenter
                obj.position = obj.lanetoenter.length  # very end of the lane
                obj.lanetoenter = None  # reset for later
                obj.bigbrother = self.parent
                obj.speed = None  # FON
                obj.acceleration = None # ^

                return True  # operation succeeded, car entered

        if type(obj) is Pedestrian:
            currgc = self.parent.gridcoords
            nextgc = obj.path[1].gridcoords
            del obj.path[0]  # we are done with this
            absolutedirection = MindController.directiontotake(currgc, nextgc)

            reldir = Intersection.getrelativedirection(self.ad, absolutedirection)

            if reldir == 0:
                obj.currtarsw = self.sw2
            if reldir == 1:
                obj.currtarsw = self.sw2  # Ontario recommends you walk on the left, for some reason
            if reldir == 2:
                obj.currtarsw = self.sw1

            obj.parent = self
            obj.bigbrother = self.parent
            obj.waitingtimeleft = 10 * obj.walkingspeed / self.length  # * 10 to convert to ticks

            self.pedwaiting.append(obj)

            return True  # operation succeeded

        return False

    def onetick(self):
        # call onetick() on all lanes and decrease Pedestrian wait time
        for l in self.lanes:
            l.onetick()

        for p in self.pedwaiting:
            p.ticksfromspawn += 1
            p.walkingtimeleft -= 1
            if p.walkingtimeleft <= 0:  # then move it to currtarsw
                p.parent = p.currtarsw
                p.currtarsw.peds.append(p)
                p.currtarsw = None  # have to decide this later
                p.justgothere = True


class Lane:
    def __init__(self, d, parent, c):
        self.cars = []  # first in the array are closest to middle of intersection
        self.direction = d  # direction is l, r, or f
        self.parentroad = parent
        self.length = c

    def isopen(self, targetroad):  # checks ZCs, Lights, etc. to see if car can go this way
        # note this tells you whether a car can drive FROM this lane, not to
        if targetroad.crossing.occupied or self.crossing.occupied:
            return False
        # TODO: check middle of intersection with predictions of where cars will be in the future

    def carcanenter(self):  # if a car in Road.offerroad()
        lastcar = self.cars[-1]
        if lastcar.position + lastcar.calcbuffer() > self.length:
            return False
        return True

    def onetick(self):
        # go through cars, based on reaction delays, speeds, etc. move them accordingly
        for c in self.cars:
            c.ticksfromspawn += 1
            c.speed += c.acceleration  # a tick is 1/10 a second

            if c.reactiondelay != None:
                c.reactiondelay -= 1
            if c.reactiondelay <= 0:  # you can never be too careful with stuff going below 0
                # figure out what to react to
                if self.cars.index(c) == 0:  # then check zebracrossing and traffic light and middle
                    if self.parentroad.crossing.occupied:  # then DEcelerate
                        d = c.position
                        s = c.speed
                        abouttotravel = d - 0.1 * s  # how many meters you will travel in the next tick
                        fractoftotal = abouttotravel / d
                        c.acceleration = round(-1 * fractoftotal * s, 1)  # exponential decay: in an n'th the distance, decrease speed by an n'th
                        # ^ rounded to one decimal place
                    if self.parentroad.parent.middle.
            # check surroundings of car
            if self.cars.index(c) == 0:  # then check Middle and ZC
                if self.parentroad.crossing.occupied:
                    distfromzc = c.position - c.minbuffer  # minbuffer because when it gets there the car's speed will be 0
                    c.howmuchtoaccelerate = Lane.calcaccel(c.speed, distfromzc, Car.weight)  # how much to DEcelerate, in this case
                    c.reactiondelay = c.reactivity

                else:
                    nextcar = self.parentroad.parent.middle.nextcarinpath()
                    if nextcar != None:  # if None then the path is almost clear, we check the Lane in the next Intersection
                        disttocar = Intersection.distfromnextcar(c.position, c.pointstooccupy, nextcar.coords)
                        c.howmuchtoaccelerate = Lane.calcaccel(c.speed, disttocar, Car.weight)
                        # LPE, last place edited
                        # now we take disttocar and figure out how much to accel/decelerate
                        # if so set the variables, if too far away, do nothing
                        # outside of if, make else, for nextcar == None, and check next Intersection in c.path,
                        # check the next lane and see if there is a car less than one car's length + buffer away from Middlem
                        # if so, figure how much to accel/decelerate
                        # if no cars in the way, do something still based off next car, probably in the next Lane in next Intersection, and decel/accelerate


    @staticmethod
    def calcaccel(speed, distfromobs, weight):
        pass


class Middle:
    # the middle of the intersection; split up into nxn squares
    # n must be even to evenly split up the roads leading in and out
    # certain square are special; e.g. some are places a car can leave or enter an intersection

    def __init__(self, parent):
        self.squares = [[None] * self.sidelength for i in range(self.sidelength)]
        self.parent = parent
        self.cars = []
        self.occupiedpoints = []  # array of points that cars or their buffer occupy at this instant
        self.tobeoccupied = []  # matrix of points that cars are going to occupy
        # ^ used with Car.position to decide right of way

    sidelength = 6 * 1000  # (FON) must be even number

    def nextcarinpath(self, path):
        pass


    def getpath(self, lane, targetroad, third):
        pass

    def onetick(self):
        pass
