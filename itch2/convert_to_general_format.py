"""
@file convert_to_general_format.py
@brief convert ITCH format to general format
@author Kael Hu @ Domeyard, winter 2016
"""

from collections import deque
import csv
import glob

def convert():
    """
    Convert ITCH5 format into general exchagne independent format.

    Args:
        None
    Returns:
        a txt file under same directory
    """
    infile_paths = glob.glob("*.csv")
    for infile_path in infile_paths:
        outfile_path = infile_path[:-4]+".txt"
        ################################### IO ##############################
        orders = []
        # read into ram

        with open(infile_path, "rb") as f:
            reader = csv.reader(f, delimiter=",")
            for i, line in enumerate(reader):
                orders.append(line)
            f.close()

        # type cast
        def type_cast(order):
            order[1] = int(order[1])
            order[2] = int(order[2])
            if order[0] == 'A':
                order[3] = float(order[3])
                order[4] = int(order[4])
            elif order[0] == 'C':
                order[3] = int(order[3])
            elif order[0] == 'R':
                order[3] = int(order[3])
                order[4] = float(order[4])
                order[5] = int(order[5])
            elif order[0] == 'T':
                order[3] = float(order[3])
                order[4] = int(order[4])
            return order

        processed_orders = []

        for order in orders:
            if len(order) > 2:
                if order[0] == 'A' and len(order) <= 5:
                    continue
                processed_orders.append(type_cast(order))

        orders = processed_orders

        ################################ IO Done ##################################

        ################################ Category #################################

        # key is the order ID
        adds = {}
        replaces = {}  # ['R', 57599020679717, 299476671, 299502429, 8.41, 100]
        cancels = {}
        trades = []  # ['T', 57598906055355, 299476711, 100]

        for order in orders:
            if order[0] == 'A':
                adds[order[2]] = order
            if order[0] == 'C':
                cancels[order[2]] = order
            if order[0] == 'R':
                replaces[order[3]] = order
            if order[0] == 'T':
                trades.append(order)

        # for cancel in cancels.values():
        #     if (cancel[2] not in adds) and (cancel[2] not in replaces):
        #         print "ghost order found."
        #     if cancel[3] != 999999:
        #         print cancel

        ######################## generate R-friendly data ########################
        #R_format_orders = [['type', 'time', 'id', 'price', 'size', 'type']]
        R_format_orders = []

        def time_to_ms(timestamp):
            return int(timestamp / 1000000.0)

        # clean replaces orders: cancel old one, add new one
        rep_values = replaces.values()
        rep_values.sort(key=lambda x: x[1])
        all_rep = deque(rep_values)

        all_orders = {}
        all_orders.update(adds)

        for _ in range(len(rep_values)):
            cur_rep = all_rep.popleft()
            if len(cur_rep) == 6:
                if cur_rep[2] in all_orders:
                    ref_order = all_orders[cur_rep[2]]
                    fake_add = ['A', cur_rep[1], cur_rep[3], cur_rep[4], cur_rep[5], ref_order[5]]
                    all_orders[fake_add[2]] = fake_add

        ###############

        for order in orders:
            if order[0] == 'A':
                R_order = ['A', time_to_ms(order[1]), order[2], order[3], order[4], ('BID' if order[5] == 'B' else 'ASK')]
                R_format_orders.append(R_order)
            elif order[0] == 'C':
                if order[3] == 999999:
                    R_order = ['C', time_to_ms(order[1]), order[2]]
                else:  # actually a replace
                    if order[2] not in all_orders:
                        continue
                    R_order = ['R', time_to_ms(order[1]), order[2], all_orders[order[2]][4] - order[3]]
                R_format_orders.append(R_order)
            elif order[0] == 'R':  # cancel old one, add new one
                if order[2] not in all_orders:
                    continue
                R_order_1 = ['C', time_to_ms(order[1]), order[2]]
                R_order_2 = ['A', time_to_ms(order[1]), order[3], order[4], order[5],
                             ('BID' if all_orders[order[2]][5] == 'B' else 'ASK')]
                R_format_orders.append(R_order_1)
                R_format_orders.append(R_order_2)
            elif order[0] == 'T':
                if order[3] == -1:
                    if order[2] in all_orders:
                        R_order = ['T', time_to_ms(order[1]), order[2], all_orders[order[2]][3], order[4]]
                    else:
                        R_order = None
                else:
                    R_order = ['T', time_to_ms(order[1]), order[2], order[3], order[4]]
                if R_order is not None:
                    R_format_orders.append(R_order)

        w = csv.writer(open(outfile_path, 'w'))
        for line in R_format_orders:
            w.writerow(line)

def main():
    convert()


if __name__ == '__main__':
    main()
