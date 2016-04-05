from utils import *

exchange_id_map = {'A': 'NYSE MKT', 'B': 'NASDAQ OMX BX', 'C': 'National Stock Exchange', 'D': 'FINRA', 'E': 'CQS',
                   'I': 'ISE', 'J': 'DirectEA', 'K': 'DirectEX', 'M': 'Chicago Stock Exchange', 'N': 'NYSE',
                   'P': 'NYSE ARCA', 'T': 'NASDAQ QMX', 'W': 'CBOE', 'X': 'NASDAQ QMX PSX', 'Y': 'BATS Y', 'Z': 'BATS'}


class CTA_header(object):
    '''
    This is the class for CTA message header (older version of length 24 bytes).
    '''

    def __init__(self, payload, all_info=False):
        '''
        init method for header class
        :param payload: header payload
        :param all_info: Bool. If True, then parse all info in the header, else only parse those useful.
        :return: None.
        '''
        self.mcat = payload[0]
        self.mtype = payload[1]
        if all_info:
            self.msg_network = payload[2]
            self.retransmission = payload[3:5]
            self.header_identifier = payload[5]
            self.reserved = payload[6:8]
            self.msg_sequence = payload[8:17]
        self.participant_id = payload[17]
        self.timestamp_raw = payload[18:24]
        self.parse_ts()

    def parse_ts(self):
        h = ord(self.timestamp_raw[0]) - ord('0')
        m = ord(self.timestamp_raw[1]) - ord('0')
        s = ord(self.timestamp_raw[2]) - ord('0')
        ms = read_ascii(self.timestamp_raw[3:6])
        self.timestamp = h * 3600 * 1000 + m * 60 * 1000 + s * 1000 + ms

    def __repr__(self):
        if hasattr(self, 'participant_id'):
            return "CTA Message Header -- " + "category: %s, type: %s, time: %s, exchange: %s" % (
                str(self.mcat), str(self.mtype), ms_to_readable_time(self.timestamp),
                exchange_id_map[self.participant_id] if self.participant_id in exchange_id_map else self.participant_id)
        else:
            return "CTA Message Header -- " + "category: %s, type: %s, time: %s" % (
                str(self.mcat), str(self.mtype), ms_to_readable_time(self.timestamp))


class CQSMessage(object):
    '''
    A class for CQS Messages
    '''

    def __init__(self, header, payload):
        '''
        init for CQS message.
        :param header: the CTAHeader class.
        :param payload: the payload for the message body
        :return: the message class
        '''
        cattype = header.mcat + header.mtype
        self.timestamp = header.timestamp
        self.type = cattype
        self.id = header.participant_id
        # TODO: round-lot size lookup
        round_lot_size = 100

        if cattype in ['ED', 'LD']:  # short quote
            self.symbol = payload[:3].split()[0]
            bid_denominator_indicator, bid_price = payload[6], payload[7:15]
            self.bid_price = CTA_price(read_ascii(bid_price), bid_denominator_indicator)
            self.bid_size = read_ascii(payload[15:18]) * round_lot_size
            ask_denominator_indicator, ask_price = payload[19], payload[20:28]
            self.ask_price = CTA_price(read_ascii(ask_price), ask_denominator_indicator)
            self.ask_size = read_ascii(payload[28:31]) * round_lot_size
            self.quote_condition = payload[3]
            self.limit_up_down_indicator = payload[4]
            self.nbbo_indicator = payload[32]
            self.finrabbo_indicator = payload[33]
            self.is_bbo = False
            if len(payload) == 62: # bbo
                self.bbo_b_id = payload[34]
                bbo_b_d, bbo_b_p = payload[35], payload[36:44]
                self.bbo_b = CTA_price(read_ascii(bbo_b_p), bbo_b_d)
                self.bbo_b_s = read_ascii(payload[44:47])
                self.bbo_a_id = payload[48]
                bbo_a_d, bbo_a_p = payload[49], payload[50:58]
                self.bbo_a = CTA_price(read_ascii(bbo_a_p), bbo_a_d)
                self.bbo_a_s = read_ascii(payload[58:61])
                self.is_bbo = True


        elif cattype in ['EB', 'BB', 'LB']:  # long quote
            self.symbol = payload[:11].split()[0]
            self.temp_suffix = payload[11]
            self.test_msg_indicator = payload[12]
            self.primary_listing_market_participant_identifier = payload[13]
            self.SIP_generated_msg_identifier = payload[14]
            self.financial_status = payload[16]
            self.currency_indicator = payload[17:20]
            self.instrument_type = payload[20]
            self.cancel_correction_indicator = payload[21]  # {'A': normal, 'B' : cancel, 'C': correction}
            self.settlement_condition = payload[22]
            self.market_condition = payload[23]
            self.quote_condition = payload[24]
            self.limit_up_down_indicator = payload[25]
            self.retail_interest_indicator = payload[26]
            bid_denominator_indicator, bid_price = payload[27], payload[28:40]
            self.bid_price = CTA_price(read_ascii(bid_price), bid_denominator_indicator)
            self.bid_size = read_ascii(payload[40:47]) * round_lot_size
            ask_denominator_indicator, ask_price = payload[47], payload[48:60]
            self.ask_price = CTA_price(read_ascii(ask_price), ask_denominator_indicator)
            self.ask_size = read_ascii(payload[60:67]) * round_lot_size
            self.finra_market_maker_id = payload[67:71]
            self.nbbo_luld_indicator = payload[72]
            self.finrabbo_luld_indicator = payload[73]
            self.short_sale_restriction_indicator = payload[74]
            self.nbbo_indicator = payload[76]
            self.finrabbo_indicator = payload[77]
            self.is_bbo = False
            if len(payload) == 136: # bbo
                self.bbo_b_id = payload[80]
                bbo_b_d, bbo_b_p = payload[81], payload[82:94]
                self.bbo_b = CTA_price(read_ascii(bbo_b_p), bbo_b_d)
                self.bbo_b_s = read_ascii(payload[94:101])
                self.finra_b_id = payload[101:104]
                self.bbo_a_id = payload[107]
                bbo_a_d, bbo_a_p = payload[108], payload[109:121]
                self.bbo_a = CTA_price(read_ascii(bbo_b_p), bbo_b_d)
                self.bbo_a_s = read_ascii(payload[121:128])
                self.finra_b_id = payload[128:132]   
                self.is_bbo = True          


    def __repr__(self):
        '''
        overrite print function
        :return: print string
        '''
        if self.type in ['ED', 'LD']:
            info = 'type: ' + str(self.type) + ', symbol: ' + str(self.symbol) + ', time: ' + ms_to_readable_time(
                self.timestamp) + ', bid: ' + str((self.bid_price, self.bid_size)) + ', ask: ' + str(
                (self.ask_price, self.ask_size))
            return info
        elif self.type in ['EB', 'BB', 'LB']:
            info = 'type: ' + str(self.type) + ', symbol: ' + str(self.symbol) + ', time: ' + ms_to_readable_time(
                self.timestamp) + ', bid: ' + str((self.bid_price, self.bid_size)) + ', ask: ' + str(
                (self.ask_price, self.ask_size))
            if self.cancel_correction_indicator == 'B':
                l_info = 'Cancel Order'
            elif self.cancel_correction_indicator == 'C':
                l_info = 'Replace Order'
            else:
                l_info = ''
            return info + ', ' + l_info
        else:
            return 'Unrelated Msgs.'

    def get_info(self):
        '''
        get necessary information from the quote
        :return: tuple of information
        '''
        if self.type in ['ED', 'LD']:
            info = (self.symbol, self.timestamp, self.bid_price, self.bid_size, self.ask_price, self.ask_size)
            return info
        elif self.type in ['EB', 'BB', 'LB']:
            info = [self.symbol, self.timestamp, self.bid_price, self.bid_size, self.ask_price, self.ask_size]
            if self.cancel_correction_indicator == 'B':
                info.append('C')
            elif self.cancel_correction_indicator == 'C':
                info.append('R')
            return tuple(info)

    def get_BBO(self):
        if self.type in ['ED', 'LD', 'EB', 'BB', 'LB'] and self.is_bbo:
            return self.symbol + ',' + 'Q' + ',' + str(int(self.timestamp / 10.0)) + ',' + str(
                self.bbo_b) + ',' + str(self.bbo_a) + ',' + str(self.bbo_b_id) + ',' + str(self.bbo_a_id)


class CTSMessage(object):
    '''
    A class for CTS Messages
    '''

    def __init__(self, header, payload):
        '''
        init for CTS message.
        :param header: the CTAHeader class.
        :param payload: the payload for the message body
        :return: the message class
        '''
        cattype = header.mcat + header.mtype
        self.timestamp = header.timestamp
        self.type = cattype
        self.id = header.participant_id

        if cattype in ['EI', 'LI']:  # short trade
            self.symbol = payload[:3].split()[0]
            self.sale_condition = payload[3]
            self.trade_volume = read_ascii(payload[4:8])
            price_demonimator_indicator, trade_price = payload[8], payload[9:17]
            self.trade_price = CTA_price(read_ascii(trade_price), price_demonimator_indicator)
            self.consolicated_hll_indicator = payload[17]
            self.participant_ohll_indicator = payload[18]

            self.info = (self.symbol, self.trade_price, self.trade_volume)


        elif cattype in ['BB', 'EB', 'LB']:  # long trade
            self.symbol = payload[:11].split()[0]
            self.temp_suffix = payload[11]
            self.test_msg_indicator = payload[12]
            self.trade_reporting_facility_identifier = payload[13]
            self.primary_listing_market_participant_identifier = payload[14]
            self.financial_status = payload[16]
            self.currency_indicator = payload[17:20]
            self.held_trade_indicator = payload[20]
            self.instrument_type = payload[21]
            self.sellers_sale_days = payload[22:25]
            self.sale_condition = payload[25:29]
            self.trade_through_exempt_indicator = payload[29]
            self.short_sale_restriction_indicator = payload[30]
            price_demonimator_indicator, trade_price = payload[32], payload[33:45]
            self.trade_price = CTA_price(read_ascii(trade_price), price_demonimator_indicator)
            self.trade_volume = read_ascii(payload[45:54])
            self.consolicated_hll_indicator = payload[54]
            self.participant_ohll_indicator = payload[55]
            self.stop_stock_indicator = payload[57]

            self.info = (
                self.symbol, self.trade_price, self.trade_volume, self.primary_listing_market_participant_identifier)

        elif cattype in ['BP', 'EP', 'LP']:  # correction
            # original information
            self.primary_listing_market_participant_identifier = payload[5]
            self.trade_reporting_facility_identifier = payload[6]
            self.symbol = payload[7:18].split()[0]
            self.temp_suffix = payload[18]
            self.financial_status = payload[19]
            self.currency_indicator = payload[20:23]
            self.instrument_type = payload[23]
            self.output_sequence_number_of_transaction_being_adjusted = payload[24:33]
            self.sellers_sale_days = payload[34:37]
            self.sale_condition = payload[37:41]
            price_demonimator_indicator, trade_price = payload[41], payload[42:54]
            self.trade_price = CTA_price(read_ascii(trade_price), price_demonimator_indicator)
            self.trade_volume = read_ascii(payload[54:63])
            self.stop_stock_indicator = payload[63]
            self.trade_through_exempt_indicator = payload[64]
            self.short_sale_restriction_indicator = payload[65]
            # corrected information
            self.sellers_sale_days_c = payload[74:77]
            self.sale_condition_c = payload[77:81]
            price_demonimator_indicator_c, trade_price_c = payload[81], payload[82:94]
            self.trade_price_c = CTA_price(read_ascii(trade_price_c), price_demonimator_indicator_c)
            self.trade_volume_c = read_ascii(payload[94:103])
            self.stop_stock_indicator_c = payload[103]
            self.trade_through_exempt_indicator_c = payload[104]
            self.short_sale_restriction_indicator_c = payload[105]
            # consolidated data
            self.last_participant_id = payload[114]
            last_price_denominator_indicator, last_price = payload[115], payload[116:128]
            self.last_price = CTA_price(read_ascii(last_price), last_price_denominator_indicator)
            self.previous_close_price_date = payload[128:134]
            high_price_denominator_indicator, high_price = payload[134], payload[135:147]
            self.high_price = CTA_price(read_ascii(high_price), high_price_denominator_indicator)
            low_price_denominator_indicator, low_price = payload[147], payload[148:160]
            self.low_price = CTA_price(read_ascii(low_price), low_price_denominator_indicator)
            self.total_volume = read_ascii(payload[160:171])
            # participant_data
            last_price_denominator_indicator_p, last_price_p = payload[182], payload[183:195]
            self.last_price_p = CTA_price(read_ascii(last_price_p), last_price_denominator_indicator_p)
            self.previous_close_price_date_p = payload[195:201]
            self.total_volume_p = read_ascii(payload[201:212])
            self.tick = payload[212]
            open_price_denominator_indicator, open_price = payload[213], payload[214:226]
            self.open_price = CTA_price(read_ascii(open_price), open_price_denominator_indicator)

            high_price_denominator_indicator_p, high_price_p = payload[226], payload[227:239]
            self.high_price_p = CTA_price(read_ascii(high_price_p), high_price_denominator_indicator_p)
            low_price_denominator_indicator_p, low_price_p = payload[239], payload[240:252]
            self.low_price_p = CTA_price(read_ascii(low_price_p), low_price_denominator_indicator_p)

            self.info = (self.symbol, self.trade_price, self.trade_volume, self.trade_price_c, self.trade_volume_c,
                         self.primary_listing_market_participant_identifier)

        elif cattype in ['BQ', 'EQ', 'LQ']:  # cancel or error
            # general trade information
            self.primary_listing_market_participant_identifier = payload[5]
            self.trade_reporting_facility_identifier = payload[6]
            self.symbol = payload[7:18].split()[0]
            self.temp_suffix = payload[18]
            self.financial_status = payload[19]
            self.currency_indicator = payload[20:23]
            self.instrument_type = payload[23]
            self.cancel_error_action = payload[24]
            self.output_sequence_number_of_transaction_being_adjusted = payload[25:34]
            # original trade information
            self.sellers_sale_days = payload[34:37]
            self.sale_condition = payload[37:41]
            price_demonimator_indicator, trade_price = payload[41], payload[42:54]
            self.trade_price = CTA_price(read_ascii(trade_price), price_demonimator_indicator)
            self.trade_volume = read_ascii(payload[54:63])
            self.stop_stock_indicator = payload[63]
            self.trade_through_exempt_indicator = payload[64]
            self.short_sale_restriction_indicator = payload[65]
            # consolidated data
            self.last_participant_id = payload[74]
            last_price_denominator_indicator, last_price = payload[75], payload[76:88]
            self.last_price = CTA_price(read_ascii(last_price), last_price_denominator_indicator)
            self.previous_close_price_date = payload[88:94]
            high_price_denominator_indicator, high_price = payload[94], payload[95:107]
            self.high_price = CTA_price(read_ascii(high_price), high_price_denominator_indicator)
            low_price_denominator_indicator, low_price = payload[107], payload[108:120]
            self.low_price = CTA_price(read_ascii(low_price), low_price_denominator_indicator)
            self.total_volume = read_ascii(payload[120:131])
            # participant data
            last_price_denominator_indicator_p, last_price_p = payload[142], payload[143:155]
            self.last_price_p = CTA_price(read_ascii(last_price_p), last_price_denominator_indicator_p)
            self.previous_close_price_date_p = payload[155:161]
            self.total_volume_p = read_ascii(payload[161:172])
            self.tick = payload[172]
            open_price_denominator_indicator, open_price = payload[173], payload[174:186]
            self.open_price = CTA_price(read_ascii(open_price), open_price_denominator_indicator)
            high_price_denominator_indicator_p, high_price_p = payload[186], payload[187:199]
            self.high_price_p = CTA_price(read_ascii(high_price_p), high_price_denominator_indicator_p)
            low_price_denominator_indicator_p, low_price_p = payload[199], payload[200:212]
            self.low_price_p = CTA_price(read_ascii(low_price_p), low_price_denominator_indicator_p)

            self.info = (self.symbol, self.trade_price, self.trade_volume, self.cancel_error_action,
                         self.primary_listing_market_participant_identifier)

        elif cattype in ['BF', 'EF', 'LF']:  # trading status
            self.symbol = payload[:11].split()[0]
            self.temp_suffix = payload[11]
            self.financial_status = payload[16]
            self.currency_indicator = payload[17:20]
            self.instrument_type = payload[20]
            self.security_status = payload[21]
            self.halt_reason = payload[22]
            self.due_to_related_security_indicator = payload[23]
            self.in_view_of_common_indicator = payload[24]
            last_price_denominator_indicator, last_price = payload[25], payload[26:38]
            self.last_price = CTA_price(read_ascii(last_price), last_price_denominator_indicator)
            self.status_indicator = payload[38]
            high_price_denominator_indicator, high_price = payload[39], payload[40:52]
            self.high_price_band = CTA_price(read_ascii(high_price), high_price_denominator_indicator)
            low_price_denominator_indicator, low_price = payload[52], payload[53:65]
            self.low_price_band = CTA_price(read_ascii(low_price), low_price_denominator_indicator)
            self.buy_volume = read_ascii(payload[66:75])
            self.sell_volume = read_ascii(payload[75:84])
            self.short_sale_restriction_indicator = payload[84]
            self.luld_indicator = payload[85]

            self.info = (self.symbol, self.security_status)

        elif cattype in ['BS', 'ES', 'LS']:  # consolidated end of day summary
            self.symbol = payload[:11].split()[0]
            # self.temp_suffix = payload[11]
            # self.financial_status = payload[12]
            # self.currency_indicator = payload[13:16]
            # self.instrument_type = payload[16]
            # self.short_sale_restriction_indicator = payload[17]
            self.last_participant_id = payload[28]
            last_price_denominator_indicator, last_price = payload[29], payload[30:42]
            self.last_price = CTA_price(read_ascii(last_price), last_price_denominator_indicator)
            self.previous_close_price_date = payload[42:48]
            high_price_denominator_indicator, high_price = payload[48], payload[49:61]
            self.high_price = CTA_price(read_ascii(high_price), high_price_denominator_indicator)
            low_price_denominator_indicator, low_price = payload[61], payload[62:74]
            self.low_price = CTA_price(read_ascii(low_price), low_price_denominator_indicator)
            self.total_volume = read_ascii(payload[74:85])
            # self.number_of_participants = payload[96:98]

            self.info = ()

        elif cattype in ['BT', 'ET', 'LT']:  # participant end of day summary
            self.symbol = payload[:11].split()[0]
            self.temp_suffix = payload[11]
            self.participant_id = payload[12]
            last_price_denominator_indicator, last_price = payload[13], payload[14:26]
            self.last_price = CTA_price(read_ascii(last_price), last_price_denominator_indicator)
            self.previous_close_price_date = payload[26:32]
            self.total_volume = read_ascii(payload[32:43])
            self.tick = payload[43]
            open_price_denominator_indicator, open_price = payload[44], payload[45:57]
            self.open_price = CTA_price(read_ascii(open_price), open_price_denominator_indicator)
            high_price_denominator_indicator, high_price = payload[57], payload[58:70]
            self.high_price = CTA_price(read_ascii(high_price), high_price_denominator_indicator)
            low_price_denominator_indicator, low_price = payload[70], payload[71:83]
            self.low_price = CTA_price(read_ascii(low_price), low_price_denominator_indicator)

            self.info = ()

            # elif cattype in ['YX']: # short index
            #     self.number_of_indices_in_group = read_ascii(payload[:2])
            #     self.index_symbol = payload[2:5].split()[0]
            #     self.index_sign = payload[6]
            #     self.index_value = read_ascii(payload[7:15]) # check this field's type
            #     self.index_symbol_group = payload[15:18].split()[0]
            #     self.index_sign_group = payload[19]
            #     self.index_value_group = read_ascii(payload[20:28])

    def __repr__(self):
        return str((self.type, ms_to_readable_time(self.timestamp)) + self.info)

    def get_BBO(self):
        if self.type in ['EI', 'LI', 'BB', 'EB', 'LB']:
            return self.symbol + ',' + 'T' + ',' + str(int(self.timestamp / 10.0)) + ',' + str(
                self.trade_price) + ',' + str(self.id)
