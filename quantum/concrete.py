# Intersection, Road, Lane, Middle - big infrastructure stuff

import entities, virtual


class Intersection:
    # an intersection consists of 4 roads and a middle; everything else is contained inside the roads
    # intersections do NOT have roads leading out of them, only in
    # once a car goes through, it immediately transfers to the next intersection

    # whichroads is a string of 4 1s and 0s telling you what roads are active, going clockwise
    # note that an inactive road is not necessarily an edge road, since the edges typically have roads for the portals
    # adj always is a tuple of 4 since if it's on the edge it has portals
    def __init__(self, gc, p):
        self.adjacents = [None] * 4  # intersections/portals adjacent to this intersection
        self.middle = Middle(self)

        self.parent = p
        self.gridcoords = gc  # used by MindController.pathfind() to figure out where it's located on the grid

        # initiates roads
        # roads are ordered clockwise, starting from top
        self.roads = []
        for i in range(4):  # b for boolean
            newroad = Road(self, i)
            self.roads.append(newroad)

        r1, r2, r3, r4 = self.roads[0], self.roads[1], self.roads[2], self.roads[3]  # for ease of use

        # set the sidewalks
        s1 = Sidewalk(self, r1.crossing, r2.crossing)  # upper right corner
        s2 = Sidewalk(self, r2.crossing, r3.crossing)  # bottom right corner
        s3 = Sidewalk(self, r3.crossing, r4.crossing)  # etc, clockwise
        s4 = Sidewalk(self, r4.crossing, r1.crossing)
        self.sidewalks = [s1, s2, s3, s4]
        self.crossings = [r1.crossing, r2.crossing, r3.crossing, r4.crossing]

        # set the road's sidewalk attributes, for Intersection.gettargetsidewalk()
        r1.sw1, r1.sw2 = s4, s1  # top
        r2.sw2, r2.sw2 = s1, s2  # right
        r3.sw2, r3.sw2 = s2, s3  # etc clockwise
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
        for r in self.roads:
            r.onetick()
        for s in self.sidewalks:
            s.onetick()
        for zc in self.crossings:
            zc.onetick()

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

        self.middle = self.parent.middle

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
                # TODO: accont for if going to portal next
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

                return True  # operation succeeded, car entered

        if type(obj) is Pedestrian: # TODO: accont for if going to portal next
            p.currtarzc = None
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
            obj.walkingtimeleft = Pedestrian.timeleft(self.length)  # * 10 to convert to ticks

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
        self.bigbrother = self.parentroad.parent
        self.length = c

    def isopen(self, targetroad):  # checks ZCs, Lights, etc. to see if car can go this way
        # note this tells you whether a car can drive FROM this lane, not to
        if targetroad.crossing.occupied or self.crossing.occupied:
            return False
        # TODO: check middle of intersection with predictions of where cars will be in the future

    def carcanenter(self):  # if a car in Road.offerroad()
        lastcar = self.cars[-1]
        if lastcar.position + Car.calcbuffer(lastcar.speed) > self.length:
            return False
        return True

    def onetick(self):
        # go through cars, based on reaction delays, speeds, etc. move them accordingly
        for c in self.cars:
            # if c.middlepath == None:  # it just entered the lane
                # TODO: finish this and figure out function call
                # c.middlepath = self.bigbrother.middle.getpath(self, )
            c.ticksfromspawn += 1

            notexec = []  # not executed, as in not run
            for r in c.reactiondelay:
                r[0] -= 1  # decrement the reaction time
                # ^ TODO: will this break because of pointers?

                if r[0] == 0:
                    c.run(r[1])  # run the command
                else:
                    notexec.append(list(r))
            del c.reactiondelay[:]  # delete everything...
            c.reactiondelay = notexec  # ... and replace it with the ones that haven't been executed

            currgc = self.bigbrother.gridcoords
            nextgc = c.path[0].gridcoords  # FIXME: should the index be 0 or 1?
            ad = MindController.directiontotake(currgc, nextgc)  # absolute direction, tells us the next intersection to take
            nextroad = self.bigbrother.roads[ad]  # car doesn't drive on this road; it drives on the adjacent road on the next intersection
            # ^ however we do cross this road's ZC, so we have to check that now

            # figure out what situation the car is in right now
            if self.cars.index(c) == 0:  # front of the Lane
                # if this crossing or nextroad.crossing occupied, brake completely, same if red light and not right turning, if yellow light, determine based on c.position and c.speed

                if self.parentroad.crossing.occupied or nextroad.crossing.occupied:
                    # figure out how much stop, set acceleration?
                    c.setdecelspeed()  # sets speed, and sometimes position

                oppositelight = self.bigbrother.getoppositeroad(self.parentroad).light
                elif oppositelight.state == 2:  # red
                    if self.direction == 'r':  # then the car still has to stop before turning, but can turn
                        if car.speed == 0 and car.position == 0:  # car is at front of lane and has stopped
                            car.speed = 2  # FON?
                            # TODO: do stuff regarding put into middle
                        else:
                            c.setdecelspeed()
                    else:
                        c.setdecelspeed()

                elif oppositelight.state == 1:  # yellow
                    # figure out whether to decelerate or keep going
                    if c.goingthroughyellow == False:
                        c.setdecelspeed()
                    elif c.goingthroughyellow == None:  # then based off c.position decide whether to go through
                        if c.speed >= c.position / 2:  # FON, but the logic here is you want to get into the Middle in less than 2 seconds
                            c.goingthroughyellow == True
                            c.speed = min(self.parentroad.speedlimit, c.speed + 1)

                    # if gtyellow is already True we don't need to do anything

                else:  # green! Hooray!
                    if self.bigbrother.middle.pathisclear(c.middlepath):
                        # make speed go up linearly to speed limit
                        c.speed = min(self.parentroad.speedlimit, c.speed + 1)
                    else:
                        # decreasing like normal
                        c.setdecelspeed()

            else:  # not first car
                # with reactiondelay, set speed of car to that of car in front unless the buffer is too small

                carinfront = self.cars[self.cars.index(c) - 1]  # the car closer to the Middle
                higherspeed = max([carinfront.speed, c.speed])  # use this to calculate the buffer
                if c.position - carinfront.position - Car.length - Car.calcbuffer(higherspeed) <= 0:  # if the cars are too close
                    # this should NEVER happen, so print to console
                    print('Dude, I hate to break it to you, but it\'s debugging time. We cannot have car crashes!')
                    exit(0)  # TODO: remove this all once debugging is done. Noe, not the whole project, just these few lines.

                comm = 'self.speed = ' + str(carinfront.speed)
                c.reactiondelay.append([Car.reactivity, comm])  # set this to be executed when the driver 'reacts'

            c.position -= c.speed / 10
            # put car into middle
            if c.position <= 0 and self.parentroad.middle.pathisclear(c.middlepath):  # go into Middle
                # we let Middle deal with directions and fun stuff, here we just dump it
                self.parentroad.middle.offermiddle(c)


class Middle:
    # the middle of the intersection; split up into nxn squares
    # n must be even to evenly split up the roads leading in and out
    # certain square are special; e.g. some are places a car can leave or enter an intersection

    def __init__(self, parent):
        self.parent = parent
        self.cars = []
        self.occupiedpoints = []  # array of points that cars or their buffer occupy at this instant
        self.tobeoccupied = []  # matrix of points that cars are going to occupy
        # ^ used with Car.position to decide right of way

    sidelength = 60  # TODO: FON?

    rightpivotmapping = {0:[-30,30], 1:[30,30], 2:[30,-30], 3:[-30,-30]}
    leftpivotmapping = {0:[30,30], 1:[30,-30], 2:[-30,-30], 3:[-30,30]}  # used in Middle.getpath()
    # ^ based off currad get center of circle (pivot)

    # TODO: finish all of these
    def nextcarinpath(self, path):
        pass

    def pathisclear(self, path):
        pass

    def getpath(self, c, lane, targetad):
        # note that targetad is the ad relative to THIS intersection, not the next in path
        # first figure out straight line or curved
        currad = lane.parentroad.absolutedirection
        if (currad + 2) % 4 == targetad:  # straight line

        elif (currad + 1) % 4 == targetad:  # left, big circle
            pass
        else:  # right, little circle
            pass


    def onetick(self):
        pass

    def offermiddle(self, c):
        # we always accept it because it's been checked beforehand
        c.parent = self
        # TODO: decide nextroad
