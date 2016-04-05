"""
@file main.py
@brief A simple parser to parse UTP feeds.
@author Chris Bao, Kael Hu
"""

from msg_class import *
from glob import glob
import sys
from msg_class import *


def main(argv):
    """
    Main function for the parser.

    Args:
        argv: list of tickers we want to parse
    Returns:
        print all messages related to the input tickers to screen
    """
    paths = glob('*.bin')
    ticker_list = []
    for ticker in argv[1:]:
        ticker_list.append(ticker)

    for path in paths:

        msgs = read_file(path)

        for i in range(len(msgs)):
            msg = msgs[i]
            header = UTP_header(msg[:24])
            body = msg[24:]

            if 'UTDF' in path:
                parsed_msg = UTDFMessage(header, body)
            elif 'UQDF' in path:
                parsed_msg = UQDFMessage(header, body)

            if hasattr(parsed_msg, 'symbol'):
                if parsed_msg.symbol in ticker_list:
                    print parsed_msg.__dict__


if __name__ == '__main__':
    main(sys.argv)
