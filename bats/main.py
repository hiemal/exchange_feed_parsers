#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@file main.py
@brief parser for BATS feed.
@author Kael Hu @ Domeyard, winter 2016
"""


import glob,textwrap,time,csv,sys
from collections import defaultdict
from struct import unpack

from msg_class import *
from utils import *
from msg_class import *

class PitchMessageReader(object):
    """
    This is a reader class. The read_message method is used to get one message from the binary file.
    """

    def __init__(self, stream):
        self.stream = stream
        self.available = 0

    def read_message(self):
        """
        Read next available message if there exists one.

        Args:
            None
        Returns:
            Message if succeed, else None.
        """
        if self.available <= 0:
            buf = self.stream.read(8)
            if buf is None or len(buf) < 8:
                return None
            length, count, unit, sequence = unpack('<HBBL', buf)
            self.available = count

        read_body = self.stream.read(2)
        if read_body is None or len(read_body) < 2:
            return None
        msg_len, msg_type = unpack('<BB', read_body)

        msg_payload = self.stream.read(msg_len - 2)

        if msg_payload:
            self.available -= 1
            return PitchMessage(msg_type, msg_payload)
        return None

    def close(self):
        """
        Close file.

        Args:
            None
        Returns:
            None
        """
        self.stream.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.close()
        except:
            pass
        return False


def main(argv):
    """
    main function for the parser.

    Args:
        argv: list of tickers
    Returns:
        save related tickers' information to a txt file.
    """
    focus_list = []
    for focus_ticker in argv[1:]:
        focus_list.append(focus_ticker)

    start = time.time()
    n = 0
    # focus_types = [0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29]

    file_paths = glob.glob('*.bin')

    # symbol related
    all_orders = {}
    all_times = {}  # {n:time_msg}

    # time
    all_time_id = []  # this is sorted.

    # need to match with add_orders
    add_order_map = {}

    #bar = tqdm('Parsing', total=250000000)  # total = 104000000 for BYX, 250000000 for BZX

    for file_path in file_paths:
        infile = open(file_path, 'rb')
        with PitchMessageReader(infile) as reader:
            while True:
                msg = reader.read_message()
                if msg is None:
                    break
                n += 1
                if hasattr(msg, 'symbol') or msg.type in [0x20, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29]:
                    if msg.type not in [0x20, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29]:
                        msg_symbol = msg.symbol.split()[0]
                        if msg_symbol in focus_list:
                            if msg_symbol not in all_orders:
                                all_orders[msg_symbol] = defaultdict(list)
                            all_orders[msg_symbol][msg.type].append((msg, n))
                            # if is add order, add to add_order_map
                            if msg.type in [0x21, 0x22, 0x2F]:
                                add_order_map[msg.order_id] = msg_symbol
                    elif msg.type == 0x20:
                        all_times[n] = msg
                        all_time_id.append(n)
                    elif msg.type in [0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29]:
                        if hasattr(msg, 'order_id'):
                            if msg.order_id in add_order_map:
                                all_orders[add_order_map[msg.order_id]][msg.type].append((msg, n))
                            else:
                                pass  # modified orders for those unrelated stocks.

                                # if n % 10000000 == 0:
                                #     bar.update(10000000)

    ######################################### build R format #########################################

    def absolutize_time(msg_tuple):
        '''
        convert time offset to absolute seconds: find time in time_array speed up search.
        Find nearest n in all_time_id, then look it up in all_time.
        The reason to enclose this into main function is for tidy concern.
        :param msg_tuple: (Message Class, id)
        :param all_times: {id: Time Message}
        :param all_time_id: sorted time message id [id, id, id, ...]
        :return: The absolute time of given input message
        '''
        time_offset = msg_tuple[0].time_offset
        id = msg_tuple[1]
        abs_time = all_times[find_lt(all_time_id, id)].time
        return abs_time + time_offset / 1000000000.0

    # convert time
    for ticker in all_orders:
        for alltype in all_orders[ticker]:
            for msgs in all_orders[ticker][alltype]:
                msgs[0].time_offset = absolutize_time(msgs)

    # convert BATS data to exchange independent data
    R_output = {}

    # ticker
    for ticker in focus_list:

        # add adds
        all_adds = {}
        for order_t in all_orders[ticker][ADD_ORDER_S]:
            add_l = order_t[0]
            add_info = ('A', int(1000 * add_l.time_offset), add_l.order_id, add_l.price, add_l.shares,
                        'BID' if add_l.side == 'B' else 'ASK')
            all_adds[add_l.order_id] = add_info

        for order_t in all_orders[ticker][ADD_ORDER_L]:
            add_l = order_t[0]
            add_info = ('A', int(1000 * add_l.time_offset), add_l.order_id, add_l.price, add_l.shares,
                        'BID' if add_l.side == 'B' else 'ASK')
            all_adds[add_l.order_id] = add_info

        if ADD_ORDER_E in all_orders[ticker]:
            for order_t in all_orders[ticker][ADD_ORDER_E]:
                add_l = order_t[0]
                add_info = ('A', int(1000 * add_l.time_offset), add_l.order_id, add_l.price, add_l.shares,
                            'BID' if add_l.side == 'B' else 'ASK')
                all_adds[add_l.order_id] = add_info

        # cancels
        cancels = []
        for order_t in all_orders[ticker][DELETE_ORDER]:
            del_order = order_t[0]
            del_info = ('C', int(1000 * del_order.time_offset), del_order.order_id)
            cancels.append(del_info)

        # replace
        replaces = []
        for order_t in all_orders[ticker][REDUCE_SIZE_L]:
            rep_order = order_t[0]
            rep_info = ('R', int(1000 * rep_order.time_offset), rep_order.order_id, rep_order.order_id,
                        all_adds[rep_order.order_id][3], all_adds[rep_order.order_id][4] - rep_order.canceled_shares)
            replaces.append(rep_info)

        for order_t in all_orders[ticker][REDUCE_SIZE_S]:
            rep_order = order_t[0]
            rep_info = ('R', int(1000 * rep_order.time_offset), rep_order.order_id, rep_order.order_id,
                        all_adds[rep_order.order_id][3], all_adds[rep_order.order_id][4] - rep_order.canceled_shares)
            replaces.append(rep_info)

        for order_t in all_orders[ticker][MODIFY_ORDER_L]:
            mod_order = order_t[0]
            rep_info = ('R', int(1000 * mod_order.time_offset), mod_order.order_id, mod_order.order_id, mod_order.price,
                        mod_order.shares)
            replaces.append(rep_info)

        for order_t in all_orders[ticker][MODIFY_ORDER_S]:
            mod_order = order_t[0]
            rep_info = ('R', int(1000 * mod_order.time_offset), mod_order.order_id, mod_order.order_id, mod_order.price,
                        mod_order.shares)
            replaces.append(rep_info)

        # trades
        trades = []
        for order_t in all_orders[ticker][ORDER_EXECUTED]:  # the execution orders, not trade ones
            trade_order = order_t[0]
            trade_info = (
                'T', int(1000 * trade_order.time_offset), trade_order.order_id, all_adds[trade_order.order_id][3],
                trade_order.executed_shares)
            trades.append(trade_info)

        for order_t in all_orders[ticker][ORDER_EXECUTED_AT_PRICE_SIZE]:
            trade_order = order_t[0]
            trade_info = (
                'T', int(1000 * trade_order.time_offset), trade_order.order_id, all_adds[trade_order.order_id][3],
                trade_order.executed_shares)
            trades.append(trade_info)

        R_output[ticker] = []
        R_output[ticker].extend(all_adds.values())
        R_output[ticker].extend(cancels)
        R_output[ticker].extend(replaces)
        R_output[ticker].extend(trades)
        R_output[ticker].sort(key=lambda x: x[1])

    ##### output part #####

    for ticker in R_output:
        w = csv.writer(open(ticker + '.txt', 'w'))
        to_write = R_output[ticker]
        for line in to_write:
            w.writerow(list(line))

    print textwrap.fill(
            'Parsed %s message(s) in %s second(s),  related orders are in total %s.' % (
                n, (time.time() - start), len(all_orders)), 120)


if __name__ == '__main__':
    main(sys.argv)
