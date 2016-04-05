"""
@file utils.py
@brief utility functions
@author Kael Hu @ Domeyard, winter 2016
"""


from bisect import bisect_left
import datetime
from struct import unpack
from msg_class import *


def epoch_to_seconds(epoch):
    """
    Convert epoch to seconds.

    Args:
        epoch: epoch
    Returns:
        seconds
    """
    time_s = str(datetime.datetime.fromtimestamp(epoch).time())
    hms_s = time_s.split(':')
    seconds = int(hms_s[0])*3600+int(hms_s[1])*60+int(hms_s[2])
    return seconds

def find_lt(a, x):
    """
    Find rightmost value less than x.

    Args:
        a: input sorted list []
        x: target value
    Returns:
        the rightmost value less than x
    """
    i = bisect_left(a, x)
    if i:
        return a[i - 1]



