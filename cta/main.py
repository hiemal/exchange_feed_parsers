"""
@file main.py
@brief A parser for CTA feed.
@author Kael Hu @ Domeyard, winter 2016
"""

from msg_class import *
from glob import glob
import sys


def main(argv):
    """
    The main function.

    Args:
        argv: list of tickers
    Returns:
        print out related messages of stocks in the argv list.
    """
    paths = glob('*.bin')

    ticker_list = []
    for ticker in argv[1:]:
        ticker_list.append(ticker)

    for path in paths:

        msgs = read_file(path)

        for i in range(len(msgs)):
            msg = msgs[i]
            header = CTA_header(msg[:24])
            body = msg[24:]

            if 'CTS' in path:
                parsed_msg = CTSMessage(header, body)
            elif 'CQS' in path:
                parsed_msg = CQSMessage(header, body)

            if hasattr(parsed_msg, 'symbol'):
                if parsed_msg.symbol in ticker_list:
                    info = parsed_msg.get_BBO()
                    if info is not None:
                        print parsed_msg.get_BBO()



if __name__ == '__main__':
    main(sys.argv)
