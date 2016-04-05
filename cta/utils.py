"""
@file utils.py
@brief utility functions for CTA and UTP feed.
@author Kael Hu @ Domeyard, winter 2016
"""

def read_ascii(str):
    """
    The function to convert long ascii string to integer.

    Args:
        str: input ascii string
    Return:
        the corresponding integer
    """
    l = len(str)
    val = 0
    for i in range(l):
        char_val = ord(str[i]) - ord('0')
        val = val * 10 + char_val
    return val


def ms_to_readable_time(ms):
    """
    Convert ms to a human readable format.

    Args:
        ms: milliseconds
    Return:
        string in HH:MM:SS.SSS format.
    """
    seconds = int(ms / 1000)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d.%s" % (h, m, s, str(ms % seconds))


def read_file(path):
    """
    Read the given file to list of msgs.

    Args:
        path: file path
    Returns:
        msgs as list, NOT SORTED IN TIME
    """
    # TODO: this function is ram intensive. Need to use old method to read msg one by one.
    f = open(path, 'r')
    content = f.read().split('\x03')[:-1]
    f.close()
    content = [msg[1:] for msg in content]  # cut \x01
    for msg in content:  # split at \x1F
        msg_us = msg.split('\x1F')
        if len(msg_us) > 1:
            for msg_more in msg_us[1:]:
                content.append(msg_more)
    return content


def CTA_price(price, denominator):
    """
    Convert CTA message's price to human readable price.

    Args:
        price: raw_price, in ascii string format
        denominator:  denominator indicator, a char, usually 'A', 'B', 'C', or 'D'
    Returns:
        correct price
    """
    if denominator == '0':
        return 0.0
    if denominator == 'I':
        return price
    power_level = ord(denominator) - ord('A') + 1
    return price / pow(10.0, power_level)
