import random
import math

# TODO: Figure Out Numbers for stuff labeled FON
# TODO: change stuff for ticks from 1/2 second to 1/10 second
# TODO: Make ticks timesd by 10
# TODO: add memoization to speed things up

class MindController:
    # this controls all the interactions of the simulation, aside from the traffic lights
    # does things like make cars move, spawn, etc.

    def __init__(self, s):
        self.sidelength = s  # not including Portals
        self.intersections = [[None] * s for _ in range(s)]
        self.initinter(s)
        self.portals = []  # for easy access
        self.ticks = 0  # time for the simulation; 1 tick is 1/10 a "second"

    def decidecolor(self, light):
        pass

    def decidedest(self, p):
        # takes portal and returns a portal which isn't on the same side
        ppos = p.position  # for convenience

        # aside from U-turns, cars never go back the same direction
        # and accuracy regarding destination choice shouldn't matter too much
        diffpos = lambda x: x.position != ppos
        allonothersides = list(filter(diffpos, self.portals))  # filter out portals on the same side as p
        dest = random.choice(allonothersides)

        return dest

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
                        portal = Portal(road, portalpos, self)
                        inter.adjacents[portalpos] = portal
                        self.portals.append(portal)
                    else:
                        inter.adjacents[coords.index([a, b])] = self.intersections[b][a]

    @staticmethod
    def directiontotake(currgc, nextgc):
        x1, x2, y1, y2 = currgc[0], currgc[1], nextgc[0], nextgc[1]
        if x1 < x2:
            return 2
        if x1 > x2:
            return 4
        if y1 < y2:
            return 3
        if y1 > y2:
            return 1

    def onetick(self):  # does everything that happens in a single tick
        # (almost?) every object has has a similar function which is called by this one
        # spawn and release cars, make everything move forwards, increments waiting counters, etc.
        for p in self.portals:
            p.onetick()

        # for


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

    def isopen(self, targetroad):  # checks ZCs, Lights, etc. to see if car car go this way
        pass

    def carcanenter(self):  # if a car in Road.offerroad()
        lastcar = self.cars[-1]
        if lastcar.position + lastcar.calcbuffer() > self.length:
            return False
        return True

    def onetick(self):
        # go through cars, based on reaction delays, speeds, etc. move them accordingly
        for c in self.cars:
            c.ticksfromspawn += 1
            if c.reactiondelay != None:  # then it must be about to stop or start
                if c.reactiondelay <= 0:  # then react based on c.howmuchtoaccelerate
                    c.acceleration += c.howmuchtoaccelerate / 10  # div 10 because it's just one tick
                else:
                    c.reactiondelay -= 1

            # check surroundings of car
            if self.cars.index(c) == 0:  # then check Middle and ZC
                if self.parentroad.crossing.occupied:
                    distfromzc = c.position - c.minbuffer  # minbuffer because when it gets there the car's speed will be 0
                    c.howmuchtoaccelerate = Lane.calcaccel(c.speed, distfromzc, Car.weight)  # how much to DEcelerate, in this case
                    c.reactiondelay = c.reactivity

                else:
                    nextcar = self.parentroad.parent.middle.nextcarinpath()
                    if nextcar != None:  # if None then the path is clear, we check the Lane in the next Intersection
                        disttocar = Intersection.distfromnextcar(c.position, c.pointstooccupy, nextcar.coords)
                        # LPE, last place edited
                        # now we take disttocar and figure out how much to accel/decelerate
                        # if so se the variables, if too far away, do nothing
                        # outside of if, make else, for nextcar == None, and check next Intersection in c.path,
                        # check the next lane and see if there is a car less than one car's length + buffer away from Middlem
                        # if so, figure how much to accel/decelerate
                        # if no cars in the way, do something still based off next car, probably in the next Lane in next Intersection, and decel/accelerate


    @staticmethod
    def calcaccel(speed, distfromobs, weight):
        pass

class ZebraCrossing:
    # where pedestrians cross; pedestrians do not move, but take x time to cross
    # since by law you aren't allowed to drive if the pedestrians are anywhere on the pavement
    # belongs to Road object

    def __init__(self, parent):  # parent is a Road
        # when a pedestrian is crossing it adds 1 to numberofpedestrians, when it leaves it subtracts 1
        # the crossing checks when numberofpedestrians == 0 and then it becomes not occupied
        self.occupied = False
        self.peds = []
        self.parentroad = parent
        self.length = None  # FON, probably should be random
        self.pedlight = Light(self)
        self.buttonpushed = False  # does what those buttons on telephone poles do IRL

    def onetick(self):
        pass


class Light:  # applies to traffic and pedestrian lights, since they are effectively the same, except in timing
    def __init__(self, parent):  # will figure out parenttype on its own
        self.state = 2  # same characters for pedestrian lights, in the matching which makes sense
        self.parenttype = 'z' if type(parent) is ZebraCrossing else 2
        self.parent = parent  # can be road or zebra crossing

        self.yellowtimeleft = None

    constyellowtime = None  # FON, the amount of time a light will be yellow


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



class Sidewalk:
    # small square at the four corners of intersections, where pedestrians stay when not crossing roads
    def __init__(self, p, c1, c2):
        self.parent = p
        self.peds = []
        self.crossing1, self.crossing2 = c1, c2

        # roads are from right to left, Sidewalk's perspective facing the Middle
        self.road1 = crossing1.parentroad
        self.road2 = crossing2.parentroad

    def onetick(self):
        pass


class Portal:  # called Portal because cars/pedestrians start and end here (there are multiple portals)
    # attaches to road of intersection
    # cars coming from the intersection go directly from Middle to Portal

    def __init__(self, road, pos, p):
        self.cars = []
        self.peds = []
        self.adjroad = road  # the road it feeds into'
        self.finished = []  # cars and peds who are done
        self.position = pos  # 0, 1, 2, 3 -> up, right, down, left, see MindController.decidedest()
        self.parent = p


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
        # TODO: make it increase the counter for how many cars/peds got through out of all time
        del self.finished[self.finished.index(c)]  # get index of c in cars, then delete that element

    def releasesome(self):
        # takes at most 1 car and all pedestrians and pushes them into the adjacent road
        c = self.cars.pop(0)
        success = self.adjroad.offerroad(c)  # if False the Lane must be full
        if not success:
            self.cars.append(c)

        # now the pedestrians
        succeeded = []  # list of stuff to remove after the next for loop
        for i in range(len(self.peds)):
            success = self.adjroad.offerroad(self.peds[i])
            if success:
                succeeded.append(self.peds[i])
        self.peds = list(succeeded)  # FIXME this area might break because of pointers
        del succeeded

    def deletefinished(self):
        self.parent.numgottenthrough += len(self.finished)
        for c in self.finished:
            self.deleteobj(c)

    def onetick(self):
        if random.random() < Portal.carprob:
            self.createcar()

        if random.random() < Portal.pedprob:
            self.createped()

        self.deletefinished()  # get rid of cars and peds who
        self.releasesome()

    carprob = None  # (FON) probability that a car will spawn in a given tick, similar below
    pedprob = None  # (FON)


class Car:
    def __init__(self, p):
        # cars spawn in Portals which are adjacent to the outer intersections
        # location == 0, 'p' is digital; 'm' is analog
        # when turning cars follow a rough circle

        self.parent = p  # either Portal, Lane, or Middle; this also tells us how it should behave
        bigbrother = self.parent.parent
        self.destination = bigbrother.decidedest(self.parent)  # the portal it wants to get to
        self.path = bigbrother.pathfind(self.parent, self.destination)  # array of Intersections followed by one Portal, the path to follow to get to self.destination
        self.ticksfromspawn = 0  # note that this is not seconds, but ticks, so always integer value
        # ^ TODO: add stuff to increment this


        # these are used in conjunction with similar fields in Middle

        # stuff used in Lane
        # FON all of this, probably research
        # TODO: decide if certain car values (reaction speed, etc.) are random? If not, make static
        # ^ similar for Pedestrians
        # ^ got from Honda Civic

        # used when in the middle of an intersection
        self.occupiedindex = None  # array of points this car occupies, from Middle.occupiedpoints
        self.pointstooccupy = None  # array of points the car will occupy, also used as path
        self.coords = [None, None]  # (0,0) is center of Intersection, x moves right, y moves up
        self.motionvector = [None, None]  # where it moves next in the Intersection; might change to direction and angle
        self.lanetoenter = None  # used in Road.offerroad()

        # used in lane
        self.position = None  # location on road, scalar
        # ^ used with self.reactivity

        self.speed = None  # m/s
        self.acceleration = None  # m/s^2
        self.howmuchtoaccelerate = None  # float, how much to accelerate/decelerate, m/s^2 (see reactiondelay)
        self.reactiondelay = None  # how long until driver should react to any incident, measured in ticks

        # constant stuff
        self.reactivity = None  # initial value for reactiondelay
        self.minb = self.length/2 + 0.5  # FON
        self.length = 449.326  # from bumper to bumper, centimeters


    def calcbuffer(self):  # calculate real buffer based on speed
        # buffer should be half of speed in mph, converted to meters
        # this way half + half of each car = correct buffer
        mph = self.speed * 1.125  # divide by 1600, multiply by 3600, divide by 2
        # ^ buts still, FON
        b = mph + self.length / 2  # car is included in this calculation
        return mph if mph > self.minb else self.minb  # so that cars don't get too close when speed is 0
        # ^ FON

    # @staticmethod
    # def deciderandvalues():
        # will return Gaussian random values for length, speed, acceleration, etc.
        # pass


class Pedestrian:
    # walking is a digital task
    # different pedestrians have different walking speeds
    # when a pedestrian walks it occupies, the crossing, stays on the same sidewalk,
    # then after x time goes to the other sidwalk and unoccupies the crossing

    def __init__(self, p):
        self.ticksfromspawn = 0  # see similar for Car
        self.walkingspeed = None  # FON or make static, m/s
        self.parent = p  # always a Sidewalk or ZebraCrossing
        self.walkingtimeleft = Pedestrian.decidewalkingspeed() # used when walking on Road or ZebraCrossing, unit seconds
        self.justgothere = False  # just got here, not just go there!
        # ^ used when just arrived at Sidewalk and wants to push button

        bigbrother = self.parent.parent
        self.destination = bigbrother.decidedest(self.parent)
        self.path = bigbrother.pathfind(self.parent, self.destination)
        self.currtarsw = None  # the current sidewalk they want to walk to

    @staticmethod
    def decidewalkingspeed():
        pass


def main():
    print('Program start')
    mc = MindController(3)  # (FON)


if __name__ == '__main__':
    main()
