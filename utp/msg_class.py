"""
@file msg_class.py
@breif UTP feed related classes
@author Chris Bao, Kael Hu
"""

from utils import *

class UTP_header(object):
    """
    This is the class for UTP message header (older version of length 24 bytes).
    """

    def __init__(self, payload, all_info=False):
        """
        Init method for header class.
        
        Args:
            payload: header payload
            all_info: Bool. If True, then parse all info in the header, else only parse those useful.
        Returns:
            None
        """
        self.mcat = payload[0]
        self.mtype = payload[1]
        if all_info:
            self.session_id = payload[2]
            self.retransmission = payload[3:5]
            self.Message_Sequence_Number = payload[5:13]
            self.Market_center_id = payload[13]
        self.timestamp_raw = payload[14:23]
        self.parse_ts()

    def parse_ts(self):
        """
        Method to parse raw tiemstamp to the real timestamp.

        Args:
            self: pointer to class.
        Returns:
            timestamp in milliseconds
        """
        h = int(self.timestamp_raw[0:2])
        m = int(self.timestamp_raw[2:4])
        s = int(self.timestamp_raw[4:6])
        ms = int(self.timestamp_raw[6:9])
        self.timestamp = h * 3600 * 1000 + m * 60 * 1000 + s * 1000 + ms

    def __repr__(self):
        return "UTP Message Header -- ", '\n', 'Category:',self.mcat,'\n','Time:', self.timestamp


class UTDFMessage(object):
    """
    A class for UTDF Messages
    """

    def __init__(self, header, payload):
        """
        Init for UTDF message.

        Args:
            header: the UTDFHeader class.
            payload: the payload for the message body
        Return:
            the message class
        """

        cattype = header.mcat + header.mtype
        self.timestamp = header.timestamp
        self.type = cattype
        round_lot_size = 100

        if cattype == 'TA' :  # short-form trade
            self.symbol = payload[0:5].split()[0]
            self.sale_condition = payload[5]
            trade_denominator_indicator, trade_price = payload[6], payload[7:13]
            self.trade_price = CTA_price(read_ascii(trade_price), trade_denominator_indicator)
            self.volume = read_ascii(payload[13:19]) * round_lot_size
            self.cons_price_change_indicator = payload[19]


        elif cattype == 'TW':  # long-form trade
            self.symbol = payload[0:11].split()[0]
            self.trade_through_exempt = payload[11]
            self.sale_condition = payload[12:16]
            self.sales_days = read_ascii(payload[16:18])
            trade_denominator_indicator, trade_price = payload[18], payload[19:29]
            self.trade_price = CTA_price(read_ascii(trade_price), trade_denominator_indicator)
            self.currency = payload[29:32]
            self.volume = read_ascii(payload[32:41]) * round_lot_size
            self.cons_price_change_indicator = payload[41]


        elif cattype == 'TY': # trade correction message
            self.original_msn = payload[0:8]
            self.symbol = payload[8:19].split()[0]
            self.original_trade_through_exempt = payload[19]
            self.original_sale_condition = payload[20:24]
            self.original_sales_days = read_ascii(payload[24:26])
            original_trade_denominator_indicator, original_trade_price = payload[26], payload[27:37]
            self.original_trade_price = CTA_price(read_ascii(original_trade_price), original_trade_denominator_indicator)
            self.original_currency = payload[37:40]
            self.original_volume = read_ascii(payload[40:49]) * round_lot_size
            self.trade_through_exempt = payload[49]
            self.sale_condition = payload[50:54]
            self.sales_days = read_ascii(payload[54:56])
            trade_denominator_indicator, trade_price = payload[56], payload[57:67]
            self.trade_price = CTA_price(read_ascii(trade_price), trade_denominator_indicator)
            self.currency = payload[67:70]
            self.volume = read_ascii(payload[70:79]) * round_lot_size
            cons_high_price_denominator_indicator, cons_high_price = payload[79], payload[80:90]
            self.cons_high_price = CTA_price(read_ascii(cons_high_price), cons_high_price_denominator_indicator)
            cons_low_price_denominator_indicator, cons_low_price = payload[90], payload[91:101]
            self.cons_low_price = CTA_price(read_ascii(cons_low_price), cons_low_price_denominator_indicator)
            cons_last_sale_price_denominator_indicator, cons_last_sale_price = payload[101], payload[102:112]
            self.cons_last_sale_price = CTA_price(read_ascii(cons_last_sale_price), cons_last_sale_price_denominator_indicator)
            self.cons_last_sale_center= payload[112]
            self.currency = payload[113:116]
            self.cons_volume = read_ascii(payload[116:127]) * round_lot_size
            self.cons_price_change_indicator = payload[127]


        elif cattype == 'TZ': # trade cancel/error
            self.original_msn = payload[0:8]
            self.symbol = payload[8:19].split()[0]
            self.functionn = payload[19]
            self.original_trade_through_exempt = payload[20]
            self.original_sale_condition = payload[21:25]
            self.original_sales_days = read_ascii(payload[25:27])
            original_trade_denominator_indicator, original_trade_price = payload[27], payload[28:38]
            self.original_trade_price = CTA_price(read_ascii(original_trade_price), original_trade_denominator_indicator)
            self.original_currency = payload[38:41]
            self.original_volume = read_ascii(payload[41:50]) * round_lot_size
            cons_high_price_denominator_indicator, cons_high_price = payload[50], payload[51:61]
            self.cons_high_price = CTA_price(read_ascii(cons_high_price), cons_high_price_denominator_indicator)
            cons_low_price_denominator_indicator, cons_low_price = payload[61], payload[62:72]
            self.cons_low_price = CTA_price(read_ascii(cons_low_price), cons_low_price_denominator_indicator)
            cons_last_sale_price_denominator_indicator, cons_last_sale_price = payload[72], payload[73:83]
            self.cons_last_sale_price = CTA_price(read_ascii(cons_last_sale_price), cons_last_sale_price_denominator_indicator)
            self.cons_last_sale_center= payload[83]
            self.currency = payload[84:87]
            self.cons_volume = read_ascii(payload[87:98]) * round_lot_size
            self.cons_price_change_indicator = payload[98]

        # the following code might be used for later
        # def __repr__(self):
        #     '''
        #     overrite print function
        #     :return: print string
        #     '''
        #     if self.type in ['ED', 'LD']:
        #         info = 'type: ' + str(self.type) + ', symbol: ' + str(self.symbol) + ', time: ' + ms_to_readable_time(
        #                 self.timestamp) + ', bid: ' + str((self.bid_price, self.bid_size)) + ', ask: ' + str(
        #                 (self.ask_price, self.ask_size))
        #         return info
        #     elif self.type in ['EB', 'BB', 'LB']:
        #         info = 'type: ' + str(self.type) + ', symbol: ' + str(self.symbol) + ', time: ' + ms_to_readable_time(
        #                 self.timestamp) + ', bid: ' + str((self.bid_price, self.bid_size)) + ', ask: ' + str(
        #                 (self.ask_price, self.ask_size))
        #         if self.cancel_correction_indicator == 'B':
        #             l_info = 'Cancel Order'
        #         elif self.cancel_correction_indicator == 'C':
        #             l_info = 'Replace Order'
        #         else:
        #             l_info = ''
        #         return info + ', ' + l_info
        #     else:
        #         return 'Unrelated Msgs.'
        #
        # def get_info(self):
        #     '''
        #     get necessary information from the quote
        #     :return: tuple of information
        #     '''
        #     if self.type in ['ED', 'LD']:
        #         info = (self.symbol, self.timestamp, self.bid_price, self.bid_size, self.ask_price, self.ask_size)
        #         return info
        #     elif self.type in ['EB', 'BB', 'LB']:
        #         info = [self.symbol, self.timestamp, self.bid_price, self.bid_size, self.ask_price, self.ask_size]
        #         if self.cancel_correction_indicator == 'B':
        #             info.append('C')
        #         elif self.cancel_correction_indicator == 'C':
        #             info.append('R')
        #         return tuple(info)


class UQDFMessage(object):
    """
    A class for UQDF Messages
    """

    def __init__(self, header, payload):
        """
        Init for UQDF message.

        Args:
            header: the UTPHeader class.
            payload: the payload for the message body
        Return:
            the message class
        """

        cattype = header.mcat + header.mtype
        self.timestamp = header.timestamp
        self.type = cattype
        round_lot_size = 100

        if cattype == 'QE' :  # short-form quotation
            self.symbol = payload[0:5].split()[0]
            self.reserved = payload[5]
            self.generated_update = payload[6]
            self.quote_condition = payload[7]
            self.LULD_BBO_indicator = payload[8]
            bid_denominator_indicator, bid_price = payload[9], payload[10:16]
            self.bid_price = round(CTA_price(read_ascii(bid_price), bid_denominator_indicator),4)
            self.bid_size = read_ascii(payload[16:18])* round_lot_size
            ask_denominator_indicator, ask_price = payload[18], payload[19:25]
            self.ask_price = round(CTA_price(read_ascii(ask_price), ask_denominator_indicator),4)
            self.ask_size = read_ascii(payload[25:27])* round_lot_size
            self.BBO_appendage_indicator = read_ascii(payload[27])
            self.LULD_BBO_appendage_indicator = payload[28]
            self.Finra_ADF_indicator = payload[29]

        if cattype == 'QF' :  # long-form quotation
            self.symbol = payload[0:11].split()[0]
            self.reserved = payload[11]
            self.generated_update = payload[12]
            self.quote_condition = payload[13]
            self.LULD_BBO_indicator = payload[14]
            self.retail_interest_indicator = payload[15]
            bid_denominator_indicator, bid_price = payload[16], payload[17:27]
            self.bid_price = round(CTA_price(read_ascii(bid_price), bid_denominator_indicator),4)
            self.bid_size = read_ascii(payload[27:34])* round_lot_size
            ask_denominator_indicator, ask_price = payload[34], payload[35:45]
            self.ask_price = round(CTA_price(read_ascii(ask_price), ask_denominator_indicator),4)
            self.ask_size = read_ascii(payload[45:52])* round_lot_size
            self.currency = payload[52:55]
            self.BBO_appendage_indicator = payload[55]
            self.LULD_BBO_appendage_indicator = payload[56]
            self.Finra_ADF_indicator = payload[57]













