from math import ceil


def area2startX(areaID):
    return ((areaID - 1) % 3) * 3 + 1

def area2startY(areaID):
    return 3 * ceil(areaID / 3) - 2