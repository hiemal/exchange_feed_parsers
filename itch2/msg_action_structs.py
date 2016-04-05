# Author: Zizhang Hu
# Date: Jan 2016
from __future__ import division
from struct import unpack
from pprint import pprint


def unpack6(message):
    """
    parse 6 bytes integer

    Args:
        message: input binary string
    Returns:
        parsed integer
    """
    uselesstail = b'\x00\x00'
    fake_message = message + uselesstail
    x1, x2, x3 = unpack('!IHH', fake_message)
    return (x1 << 16) | x2


def make_timestamp_readable(timestamp):
    """
    convert timestamp to a human readable format

    Args:
        timestamp: nanoseconds
    Returns:
        string in HH:MM:SS format.
    """
    seconds = int(timestamp / 1000000000)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


def parse(message, focus_only_stock=False):
    """
    parse raw message to message structs.

    Args:
        message: raw message
        focus_only_stock: Bool, if only process stock-related market messages.
    Returns:
        the message struct, i.e., SystemEventMessage. If None, then not msg we concern.
    """
    if len(message) == 0:
        return None
    mtype = message[0]
    

    if not focus_only_stock:
        # parse all message
        focus_mtypes = ('S', 'R', 'H', 'Y', 'L', 'V', 'W', 'K', 'A', 'F', 'E', 'C', 'X', 'D', 'U', 'P', 'Q', 'B', 'I')
    else:
        focus_mtypes = ('A', 'F', 'E', 'C', 'X', 'D', 'U', 'P', 'Q')

    if mtype in focus_mtypes:
        if mtype == 'S':
            return SystemEventMessage(message)
        elif mtype == 'R':
            return StockDirectory(message)
        elif mtype == 'H':
            return StockTradingAction(message)
        elif mtype == 'Y':
            return RegSHOShortSalePTRIndicator(message)
        elif mtype == 'L':
            return MarketParticipantPosition(message)
        elif mtype == 'V':
            return MWCBDeclineLvlMsg(message)
        elif mtype == 'W':
            return MWCBStatusMsg(message)
        elif mtype == 'K':
            return IPOQuotingPeriodUpdate(message)
        elif mtype == 'A':
            return AddOrderNoMPID(message)
        elif mtype == 'F':
            return AddOrderWithMPID(message)
        elif mtype == 'E':
            return OrderExecuteMsg(message)
        elif mtype == 'C':
            return OrderExecutedWithPriceMsg(message)
        elif mtype == 'X':
            return OrderCancelMsg(message)
        elif mtype == 'D':
            return OrderDeleteMsg(message)
        elif mtype == 'U':
            return OrderReplaceMsg(message)
        elif mtype == 'P':
            return NonCrossTradeMsg(message)
        elif mtype == 'Q':
            return CrossTradeMsg(message)
        elif mtype == 'B':
            return BrokenTradeMsg(message)
        elif mtype == 'I':
            return NetOrderImbalanceIndicatorMsg(message)
        else:
            return
    else:
        return None


class Message(object):
    """
    An abstract class for messages. All the message classes are actually C-like structs.
    """
    mtype = ''
    stockLocate = 0
    timestamp = 0
    trackingNum = 0

    def debug(self):
        pprint(vars(self))


class SystemEventMessage(Message):
    def __init__(self, message):
        self.mtype = 'S'
        self.stockLocate = 0
        trackingNumBinary = message[3:5]
        timestampBinary = message[5:11]
        eventCodeBinary = message[11]
        self.trackingNum = unpack('!H', trackingNumBinary)[0]
        self.timestamp = unpack6(timestampBinary)
        self.eventCode = eventCodeBinary


class StockDirectory(Message):
    def __init__(self, message):
        self.mtype = 'R'
        stockLocateBinary = message[1:3]
        self.stockLocate = unpack('!H', stockLocateBinary)[0]
        trackingNumBinary = message[3:5]
        self.trackingNum = unpack('!H', trackingNumBinary)[0]
        timestampBinary = message[5:11]
        self.timestamp = unpack6(timestampBinary)
        self.stock = message[11:19]
        self.marketCat = message[19]
        self.financialSatsIndicator = message[20]
        roundLotSizeBinary = message[21:25]
        self.roundLotSize = unpack('!L', roundLotSizeBinary)[0]
        self.roundLotsOnly = message[25]
        self.issueClassification = message[26]
        self.issueSubType = message[27:29]
        self.authenticity = message[29]
        self.shortSaleThrshdIndicator = message[30]
        self.IPOFlag = message[31]
        self.LULDReferencePriceTier = message[32]
        self.ETPFlag = message[33]
        ETPLeverageFactorBinary = message[34:38]
        self.ETPLeverageFactor = unpack('!L', ETPLeverageFactorBinary)[0]
        self.inverseIndicator = message[38]


class StockTradingAction(Message):
    def __init__(self, message):
        self.mtype = 'H'
        stockLocateBinary = message[1:3]
        self.stockLocate = unpack('!H', stockLocateBinary)[0]
        trackingNumBinary = message[3:5]
        self.trackingNum = unpack('!H', trackingNumBinary)[0]
        timestampBinary = message[5:11]
        self.timestamp = unpack6(timestampBinary)
        self.stock = message[11:19]
        self.tradingState = message[19]
        self.reserved = message[20]
        self.reason = message[21:25]


class RegSHOShortSalePTRIndicator(Message):
    def __init__(self, message):
        self.mtype = 'Y'
        stockLocateBinary = message[1:3]
        self.stockLocate = unpack('!H', stockLocateBinary)[0]
        trackingNumBinary = message[3:5]
        self.trackingNum = unpack('!H', trackingNumBinary)[0]
        timestampBinary = message[5:11]
        self.timestamp = unpack6(timestampBinary)
        self.stock = message[11:19]
        self.RegSHOAction = message[19]


class MarketParticipantPosition(Message):
    def __init__(self, message):
        self.mtype = 'L'
        stockLocateBinary = message[1:3]
        self.stockLocate = unpack('!H', stockLocateBinary)[0]
        trackingNumBinary = message[3:5]
        self.trackingNum = unpack('!H', trackingNumBinary)[0]
        timestampBinary = message[5:11]
        self.timestamp = unpack6(timestampBinary)
        self.MPID = message[11:15]
        self.stock = message[15:23]
        self.primaryMarketMaker = message[23]
        self.marketMakerMode = message[24]
        self.marketParticipantState = message[25]


class MWCBDeclineLvlMsg(Message):
    def __init__(self, message):
        self.mtype = 'V'
        stockLocateBinary = message[1:3]
        self.stockLocate = unpack('!H', stockLocateBinary)[0]
        trackingNumBinary = message[3:5]
        self.trackingNum = unpack('!H', trackingNumBinary)[0]
        timestampBinary = message[5:11]
        self.timestamp = unpack6(timestampBinary)
        level1binary = message[11:19]
        level2binary = message[19:27]
        level3binary = message[27:35]
        self.level1 = unpack('!Q', level1binary)[0] / 100000000.0
        self.level2 = unpack('!Q', level2binary)[0] / 100000000.0
        self.level3 = unpack('!Q', level3binary)[0] / 100000000.0


class MWCBStatusMsg(Message):
    def __init__(self, message):
        self.mtype = 'W'
        stockLocateBinary = message[1:3]
        self.stockLocate = unpack('!H', stockLocateBinary)[0]
        trackingNumBinary = message[3:5]
        self.trackingNum = unpack('!H', trackingNumBinary)[0]
        timestampBinary = message[5:11]
        self.timestamp = unpack6(timestampBinary)
        self.breachedLevel = message[11]


class IPOQuotingPeriodUpdate(Message):
    def __init__(self, message):
        self.mtype = 'K'
        stockLocateBinary = message[1:3]
        self.stockLocate = unpack('!H', stockLocateBinary)[0]
        trackingNumBinary = message[3:5]
        self.trackingNum = unpack('!H', trackingNumBinary)[0]
        timestampBinary = message[5:11]
        self.timestamp = unpack6(timestampBinary)
        self.stock = message[11:19]
        IPOQuotationReleaseTimeBinary = message[19:23]
        self.IPOQuotationReleaseTime = unpack('!L', IPOQuotationReleaseTimeBinary)[0]  # in SECONDS since midnight..WTF
        self.IPOQuotationReleaseQualifier = message[23]
        IPOPriceBinary = message[24:28]
        self.IPOPrice = unpack('!L', IPOPriceBinary)[0] / 10000.0


class AddOrderNoMPID(Message):
    def __init__(self, message):
        self.mtype = 'A'
        stockLocateBinary = message[1:3]
        self.stockLocate = unpack('!H', stockLocateBinary)[0]
        trackingNumBinary = message[3:5]
        self.trackingNum = unpack('!H', trackingNumBinary)[0]
        timestampBinary = message[5:11]
        self.timestamp = unpack6(timestampBinary)
        orderRefNumBinary = message[11:19]
        self.orderRefNum = unpack('!Q', orderRefNumBinary)[0]
        self.buySellIndicator = message[19]
        sharesBinary = message[20:24]
        self.shares = unpack('!L', sharesBinary)[0]
        self.stock = message[24:32]
        priceBinary = message[32:36]
        self.price = unpack('!L', priceBinary)[0] / 10000.0


class AddOrderWithMPID(Message):
    def __init__(self, message):
        self.mtype = 'F'
        stockLocateBinary = message[1:3]
        self.stockLocate = unpack('!H', stockLocateBinary)[0]
        trackingNumBinary = message[3:5]
        self.trackingNum = unpack('!H', trackingNumBinary)[0]
        timestampBinary = message[5:11]
        self.timestamp = unpack6(timestampBinary)
        orderRefNumBinary = message[11:19]
        self.orderRefNum = unpack('!Q', orderRefNumBinary)[0]
        self.buySellIndicator = message[19]
        sharesBinary = message[20:24]
        self.shares = unpack('!L', sharesBinary)[0]
        self.stock = message[24:32]
        priceBinary = message[32:36]
        self.price = unpack('!L', priceBinary)[0] / 10000.0
        self.attribution = message[36:40]


class OrderExecuteMsg(Message):
    def __init__(self, message):
        self.mtype = 'E'
        stockLocateBinary = message[1:3]
        self.stockLocate = unpack('!H', stockLocateBinary)[0]
        trackingNumBinary = message[3:5]
        self.trackingNum = unpack('!H', trackingNumBinary)[0]
        timestampBinary = message[5:11]
        self.timestamp = unpack6(timestampBinary)
        orderRefNumBinary = message[11:19]
        self.orderRefNum = unpack('!Q', orderRefNumBinary)[0]
        executedSharesBinary = message[19:23]
        self.executedShares = unpack('!L', executedSharesBinary)[0]
        matchNumBinary = message[23:31]
        self.matchNum = unpack('!Q', matchNumBinary)[0]


class OrderExecutedWithPriceMsg(Message):
    def __init__(self, message):
        self.mtype = 'C'
        stockLocateBinary = message[1:3]
        self.stockLocate = unpack('!H', stockLocateBinary)[0]
        trackingNumBinary = message[3:5]
        self.trackingNum = unpack('!H', trackingNumBinary)[0]
        timestampBinary = message[5:11]
        self.timestamp = unpack6(timestampBinary)
        orderRefNumBinary = message[11:19]
        self.orderRefNum = unpack('!Q', orderRefNumBinary)[0]
        executedSharesBinary = message[19:23]
        self.executedShares = unpack('!L', executedSharesBinary)[0]
        matchNumBinary = message[23:31]
        self.matchNum = unpack('!Q', matchNumBinary)[0]
        self.printable = message[31]
        executionPriceBinary = message[32:36]
        self.executionPrice = unpack('!L', executionPriceBinary)[0] / 10000.0


class OrderCancelMsg(Message):
    def __init__(self, message):
        self.mtype = 'X'
        stockLocateBinary = message[1:3]
        self.stockLocate = unpack('!H', stockLocateBinary)[0]
        trackingNumBinary = message[3:5]
        self.trackingNum = unpack('!H', trackingNumBinary)[0]
        timestampBinary = message[5:11]
        self.timestamp = unpack6(timestampBinary)
        orderRefNumBinary = message[11:19]
        self.orderRefNum = unpack('!Q', orderRefNumBinary)[0]
        canceledSharesBinary = message[19:23]
        self.canceledShares = unpack('!L', canceledSharesBinary)[0]


class OrderDeleteMsg(Message):
    def __init__(self, message):
        self.mtype = 'D'
        stockLocateBinary = message[1:3]
        self.stockLocate = unpack('!H', stockLocateBinary)[0]
        trackingNumBinary = message[3:5]
        self.trackingNum = unpack('!H', trackingNumBinary)[0]
        timestampBinary = message[5:11]
        self.timestamp = unpack6(timestampBinary)
        orderRefNumBinary = message[11:19]
        self.orderRefNum = unpack('!Q', orderRefNumBinary)[0]


class OrderReplaceMsg(Message):
    def __init__(self, message):
        self.mtype = 'U'
        stockLocateBinary = message[1:3]
        self.stockLocate = unpack('!H', stockLocateBinary)[0]
        trackingNumBinary = message[3:5]
        self.trackingNum = unpack('!H', trackingNumBinary)[0]
        timestampBinary = message[5:11]
        self.timestamp = unpack6(timestampBinary)
        oldRefNumBinary = message[11:19]
        self.oldRefNum = unpack('!Q', oldRefNumBinary)[0]
        newRefNumBinary = message[19:27]
        self.newRefNum = unpack('!Q', newRefNumBinary)[0]
        sharesBinary = message[27:31]
        self.shares = unpack('!L', sharesBinary)[0]
        priceBinary = message[31:35]
        self.price = unpack('!L', priceBinary)[0] / 10000.0


class NonCrossTradeMsg(Message):
    def __init__(self, message):
        self.mtype = 'P'
        stockLocateBinary = message[1:3]
        self.stockLocate = unpack('!H', stockLocateBinary)[0]
        trackingNumBinary = message[3:5]
        self.trackingNum = unpack('!H', trackingNumBinary)[0]
        timestampBinary = message[5:11]
        self.timestamp = unpack6(timestampBinary)
        orderRefNumBinary = message[11:19]
        self.orderRefNum = unpack('!Q', orderRefNumBinary)[0]
        self.buySellIndicator = message[19]
        sharesBinary = message[20:24]
        self.shares = unpack('!L', sharesBinary)[0]
        self.stock = message[24:32]
        priceBinary = message[32:36]
        self.price = unpack('!L', priceBinary)[0] / 10000.0
        matchNumBinary = message[36:44]
        self.matchNum = unpack('!Q', matchNumBinary)[0]


class CrossTradeMsg(Message):
    def __init__(self, message):
        self.mtype = 'Q'
        stockLocateBinary = message[1:3]
        self.stockLocate = unpack('!H', stockLocateBinary)[0]
        trackingNumBinary = message[3:5]
        self.trackingNum = unpack('!H', trackingNumBinary)[0]
        timestampBinary = message[5:11]
        self.timestamp = unpack6(timestampBinary)
        sharesBinary = message[11:19]
        self.shares = unpack('!Q', sharesBinary)[0]
        self.stock = message[19:27]
        crossPriceBinary = message[27:31]
        self.crossPrice = unpack('!L', crossPriceBinary)[0] / 10000.0
        matchNumBinary = message[31:39]
        self.matchNum = unpack('!Q', matchNumBinary)[0]
        self.crossType = message[39]


class BrokenTradeMsg(Message):
    def __init__(self, message):
        self.mtype = 'B'
        stockLocateBinary = message[1:3]
        self.stockLocate = unpack('!H', stockLocateBinary)[0]
        trackingNumBinary = message[3:5]
        self.trackingNum = unpack('!H', trackingNumBinary)[0]
        timestampBinary = message[5:11]
        self.timestamp = unpack6(timestampBinary)
        matchNumBinary = message[11:19]
        self.matchNum = unpack('!Q', matchNumBinary)[0]


class NetOrderImbalanceIndicatorMsg(Message):
    def __init__(self, message):
        self.mtype = 'I'
        stockLocateBinary = message[1:3]
        self.stockLocate = unpack('!H', stockLocateBinary)[0]
        trackingNumBinary = message[3:5]
        self.trackingNum = unpack('!H', trackingNumBinary)[0]
        timestampBinary = message[5:11]
        self.timestamp = unpack6(timestampBinary)
        pairedSharesBinary = message[11:19]
        self.pairedShares = unpack('!Q', pairedSharesBinary)[0]
        imbalanceSharesBinary = message[19:27]
        self.imbalanceShares = unpack('!Q', imbalanceSharesBinary)[0]
        self.imbalanceDirection = message[27]
        self.stock = message[28:36]
        fairPriceBinary = message[36:40]
        self.fairPrice = unpack('!L', fairPriceBinary)[0] / 10000.0
        nearPriceBinary = message[40:44]
        self.nearPrice = unpack('!L', nearPriceBinary)[0] / 10000.0
        currentRefPriceBinary = message[44:48]
        self.currentRefPrice = unpack('!L', currentRefPriceBinary)[0] / 10000.0
        self.crossType = message[48]
        self.priceVariationIndicator = message[49]


def msg_to_action(parsed_msg):
    # return None if not trade related msgs.
    add_types = ['A', 'F']
    cancel_types = ['D', 'X']
    replace_types = ['U']
    mtype = parsed_msg.mtype
    if mtype in add_types:
        return AddAction(parsed_msg)
    elif mtype in cancel_types:
        return CancelAction(parsed_msg)
    elif mtype in replace_types:
        return ReplaceAction(parsed_msg)
    elif mtype == 'E' or (mtype == 'C' and parsed_msg.printable == 'Y'):
        return TradeAction(parsed_msg)
    else:
        return None


class Action(object):
    # only for reference, abstract class for actions
    # action class is a second-level abstract for market parsed_msgs

    type = ''
    stockLocate = 0
    timestamp = 0
    orderRefNum = 0

    def debug(self):
        pprint(vars(self))


class AddAction(Action):
    def __init__(self, parsed_msg):
        self.type = 'A'
        self.stockLocate = parsed_msg.stockLocate
        self.direction = parsed_msg.buySellIndicator  # 'B' for Bid or 'S' for Ask
        self.orderRefNum = parsed_msg.orderRefNum
        self.timestamp = parsed_msg.timestamp
        self.price = parsed_msg.price
        self.size = parsed_msg.shares

    def summary(self):
        return (self.type, self.timestamp, self.orderRefNum, self.price, self.size, self.direction)


class ReplaceAction(Action):
    def __init__(self, parsed_msg):
        self.type = 'R'
        self.stockLocate = parsed_msg.stockLocate
        self.timestamp = parsed_msg.timestamp
        self.orderRefNum = parsed_msg.oldRefNum
        self.newRefNum = parsed_msg.newRefNum
        self.size = parsed_msg.shares
        self.price = parsed_msg.price

    def summary(self):
        return (self.type, self.timestamp, self.orderRefNum, self.newRefNum, self.price, self.size)


class TradeAction(Action):
    def __init__(self, parsed_msg):
        self.type = 'T'
        self.stockLocate = parsed_msg.stockLocate
        self.orderRefNum = parsed_msg.orderRefNum
        self.timestamp = parsed_msg.timestamp
        self.size = parsed_msg.executedShares
        # if price = -1, we need to infer the price from orderbook.
        # else, the price is differ from what it should be.
        if parsed_msg.mtype == 'C':
            self.price = parsed_msg.executionPrice
        else:
            self.price = -1

    def summary(self):
        return (self.type, self.timestamp, self.orderRefNum, self.price, self.size)


class CancelAction(Action):
    def __init__(self, parsed_msg):
        self.type = 'C'
        self.stockLocate = parsed_msg.stockLocate
        self.orderRefNum = parsed_msg.orderRefNum
        self.timestamp = parsed_msg.timestamp
        # if canceledShares = 999999, then cancel all shares.
        # else, cancel given shares
        if parsed_msg.mtype == 'X':
            self.size = parsed_msg.canceledShares
        else:
            self.size = 999999

    def summary(self):
        return (self.type, self.timestamp, self.orderRefNum, self.size)
