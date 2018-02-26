# Cars and Pedestrians

import virtual, concrete


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

        self.speed = None  # m/s, always multiple of 5
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
