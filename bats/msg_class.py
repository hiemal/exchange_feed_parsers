"""
@file msg_class.py
@brief message classes for BATS feed
@author Kael Hu @ Domeyard, winter 2016
"""

from struct import unpack
from utils import epoch_to_seconds


LOGIN = 0x00  # 0x01
TIME = 0x20
ADD_ORDER_L = 0x21
ADD_ORDER_S = 0x22
ADD_ORDER_E = 0x2F
ORDER_EXECUTED = 0x23
ORDER_EXECUTED_AT_PRICE_SIZE = 0x24
REDUCE_SIZE_L = 0x25
REDUCE_SIZE_S = 0x26
MODIFY_ORDER_L = 0x27
MODIFY_ORDER_S = 0x28
DELETE_ORDER = 0x29
TRADE_L = 0x2A
TRADE_S = 0x2B
TRADE_BREAK = 0x2C
END_OF_SESSION = 0x2D
TRADE_E = 0x2F
TRADING_STATUS = 0x31
UNIT_CLEAR = 0x97
RETAIL_PRICE_IMPROVEMENT = 0x98

MESSAGE_DESCRIPTIONS = {0x00: 'Login', 0x20: 'Time', 0x21: 'Add Order - Long', 0x22: 'Add Order - Short',
                        0x23: 'Order Executed', 0x24: 'Order Executed at Price/Size',
                        0x25: 'Reduce Size - Long', 0x26: 'Reduce Size - Short', 0x27: 'Modify Order - Long',
                        0x28: 'Modify Order - Short',
                        0x29: 'Delete Order', 0x2A: 'Trade - Long', 0x2B: 'Trade - Short', 0x2C: 'Trade Break',
                        0x30: 'Trade - Expanded',
                        0x2D: 'End of Session', 0x31: 'Trading Status', 0x97:'Unit Clear',0x98: 'Retail Price Improvement'}


class PitchMessage(object):
    """
    Class for PITCH messages.
    """
    def __init__(self, type, payload):
        self.type = type
        self.payload = payload
        if type == LOGIN:
            pass
        elif type == TIME:
            if len(self.payload) == 4:
                self.time = unpack('<L', payload)[0]
            elif len(self.payload) == 8:
                epoch = unpack('<Q', payload)[0]
                self.time = epoch_to_seconds(epoch)
        elif type == ADD_ORDER_L:
            if len(payload) == 32:
                self.time_offset, self.order_id, self.side, self.shares, self.symbol, self.price, self.add_flags = unpack(
                '<LQcL6sQB', payload)
        elif type == ADD_ORDER_S:
            if len(payload) == 24:
                self.time_offset, self.order_id, self.side, self.shares, self.symbol, self.price, self.add_flags = unpack(
                '<LQcH6sHB', payload)
                self.price /= 100.0
        elif type == ADD_ORDER_E:
            if len(payload) == 38:
                self.time_offset, self.order_id, self.side, self.shares, self.symbol, self.price, self.add_flags, self.participantID = unpack(
                '<LQcL8sQB4s', payload)
        elif type == ORDER_EXECUTED:
            if len(payload) == 24:
                self.time_offset, self.order_id, self.executed_shares, self.execution_id = unpack('<LQLQ', payload)
        elif type == ORDER_EXECUTED_AT_PRICE_SIZE:
            if len(payload) == 36:
                self.time_offset, self.order_id, self.executed_shares, self.remaining_shares, self.execution_id, self.price = unpack(
                '<LQLLQQ', payload)
        elif type == REDUCE_SIZE_L:
            if len(payload) == 16:
                self.time_offset, self.order_id, self.canceled_shares = unpack('<LQL', payload)
        elif type == REDUCE_SIZE_S:
            if len(payload) == 14:
                self.time_offset, self.order_id, self.canceled_shares = unpack('<LQH', payload)
        elif type == MODIFY_ORDER_L:
            if len(payload) == 25:
                self.time_offset, self.order_id, self.shares, self.price, self.modify_flags = unpack('<LQLQB', payload)
        elif type == MODIFY_ORDER_S:
            if len(payload) == 17:
                self.time_offset, self.order_id, self.shares, self.price, self.modify_flags = unpack('<LQHHB', payload)
                self.price /= 100.0
        elif type == DELETE_ORDER:
            if len(self.payload) == 12:
                self.time_offset, self.order_id = unpack('<LQ', payload)
        elif type == TRADE_L:
            if len(self.payload) == 39:
                self.time_offset, self.order_id, self.side, self.shares, self.symbol, self.price, self.execution_id = unpack( '<LQcL6sQQ', payload)
        elif type == TRADE_S:
            if len(self.payload) == 31:
                self.time_offset, self.order_id, self.side, self.shares, self.symbol, self.price, self.execution_id = unpack(
                '<LQcH6sHQ', payload)
                self.price /= 100.0
        elif type == TRADE_BREAK:
            if len(payload) == 12:
                self.time_offset, self.execution_id = unpack('<LQ', payload)
            pass
        elif type == TRADE_E:
            if len(payload) == 41:
                self.time_offset, self.order_id, self.side, self.shares, self.symbol, self.price, self.execution_id = unpack(
                '<LQcL8sQQ', payload)
        elif type == END_OF_SESSION:
            if len(payload) == 4:
                self.time_offset = unpack('<L', payload)[0]
        elif type == TRADING_STATUS:
            if len(payload) == 16:
                self.time_offset, self.symbol, self.trading_status, self.reg_sho_action, self.reserved1, self.reserved2 = unpack(
                '<L8scccc', payload)
        elif type == RETAIL_PRICE_IMPROVEMENT:
            pass
        elif type == UNIT_CLEAR:
            pass
        else:
            pass
            #raise ValueError('Invalid message type: %s', type)

    def __repr__(self):
        return '%s %s %s' % (self.__class__.__name__, MESSAGE_DESCRIPTIONS[self.type].upper(), self.__dict__)
