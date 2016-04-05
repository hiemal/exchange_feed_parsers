"""
@file stocklocate_lookup.py
@brief look up stock locate from ticker
@author Kael Hu @ Domeyard, winter 2016
"""

import sys
import glob
from collections import deque

from msg_reader_class import *

def lookup(argv):
    """
    Lookup stock_locate number from ticker

    Args:
        argv: ticker list
    Returns:
        print dict of {ticker: stock}
    """
    environ_setup = {}
    environ_setup['file_lst'] = glob.glob("*.bin")
    lookups = deque()
    inputs = []
    for ticker in argv[1:]:
        lookups.append(ticker)
        inputs.append(ticker)

    # reader
    test = MsgReader()
    test.set_path(environ_setup['file_lst'])

    # stockLoate Map
    stockLocateMap = {}

    # output
    output = {}
    ret = []
    while True:
        has_next_file = test.read_next_file_in_list()
        if not has_next_file:
            break
        while True:
            message = test.fetch_one(focus_only_stock=True)
            if message == -1:
                break
            if message is None: # not the msg type we care
                continue

            if message.mtype == 'A':
                stockLocateMap[message.stock.split()[0]] = message.stockLocate

            if len(lookups) == 0:
                print output
                ret_p = ''
                for t in inputs:
                    ret.append(output[t])
                    ret_p = ret_p + str(output[t]) + ' '
                print ret_p
                return ret
            else:
                for ticker in list(lookups):
                    if ticker in stockLocateMap:
                        output[ticker] = stockLocateMap[ticker]
                        lookups.remove(ticker)

def main(argv):
    lookup(argv)


if __name__ == '__main__':
    main(sys.argv)