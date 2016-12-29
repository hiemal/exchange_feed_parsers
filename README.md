# Direct Feed Parsers for NASDAQ, BATS, CTA, and UTP



## Parsers
ITCH2 is the parser for Nasdaq ITCH 5.0. BATS is the parser for BATS PITCH. CTA is the parser for CTS and CQS, while UTP is the parser for UTDF and UQDF.

All parsers in together support following feed formats:
- Nasdaq ITCH 5.0, includes BX and PSX
- BATS PITCH, includes BYX, BZX, EDGA, and EDGX
- CTA and UTP, includes CQS, CTS, UQDF, UTDF

The input feed is in pcap format, thus in each parser's directory, there is a bash file to convert it to the binary file for parsers to read.

Then each parser outputs an exchange-independent transactions text file. In this file, orders are categorized into four types: Add, Cancel, Replace, Trade. The first column is the type of transaction ('A', 'C', 'R', 'T'), the second column is the timestamp in 10 ms. The third column is the order ID.
