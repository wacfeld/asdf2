import random
import math

import asides, concrete, entities

# TODO: Figure Out Numbers for stuff labeled FON
# TODO: change stuff for ticks from 1/2 second to 1/10 second
# TODO: Make ticks timesd by 10
# TODO: add memoization to speed things up

# A few unit definitions:
# a tick is 1/10 a second
# speed is measured in m/s, acceleration in m/s^2
# distance is measured in m
# time increments by 0.1 s, distance by 0.1 m, similar for speed and acceleration
# drivers have reaction delay of 300 ms, pedestrians 0


def main():
    print('Program start')
    mc = MindController(3)  # (FON)


if __name__ == '__main__':
    main()
