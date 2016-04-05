"""
@file main.py
@brief Nasdaq ITCH 5.0 parser
@author Kael Hu @ Domeyard, winter 2016
"""

import sys
import glob
from collections import defaultdict
import csv

from convert_to_general_format import convert
from msg_reader_class import *

def parse_stocks(argv):
    """
    Parse stock locate.

    Args:
        argv: list of stock locate numbers
    Returns:
        None. Save related message information in to a csv file.
    """

    environ_setup = {}
    environ_setup['file_lst'] = glob.glob("*.bin")
    environ_setup['target_stocks'] = []
    for stockLocate in argv[1:]:
        environ_setup['target_stocks'].append(int(stockLocate))

    # reader
    test = MsgReader()
    test.set_path(environ_setup['file_lst'])

    # related_actions
    related_actions = defaultdict(list)

    # stockLoate Map
    stockLocateMap = {}

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

            if message.stockLocate in environ_setup['target_stocks']:
                action = msg_to_action(message)
                if action is not None:
                    related_actions[action.stockLocate].append(action.summary())

    for ticker in related_actions:
        ticker_lst = related_actions[ticker]
        w = csv.writer(open("Nasdaq_"+str(ticker)+".csv",'w'))
        for line in ticker_lst:
            w.writerow(list(line))

def main(argv):
    """
    main function for ITCH 5.0 parser.
    """
    parse_stocks(argv)
    convert()


if __name__ == '__main__':
    main(sys.argv)