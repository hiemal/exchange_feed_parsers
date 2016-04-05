# Direct Feed Parsers for NASDAQ, BATS, CTA, and UTP
###### Zizhang Hu @ Domeyard LP, winter 2016

## Introduction
This project is done by the author in Winter 2016. [Domeyard](http://www.domeyard.com/) is an awesome Boston based trading firm where the author did research internship sponsored by MIT Sloan.

__This project is a student project of a business school. The author has no background in either software engineering or quant development. The awful code style and chaotic project structure does not align with the average skill level of Domeyard. This project is not used by Domeyard after this winter project.__

## Parsers
ITCH2 is the parser for Nasdaq ITCH 5.0. BATS is the parser for BATS PITCH. CTA is the parser for CTS and CQS, while UTP is the parser for UTDF and UQDF.

All parsers in together support following feed formats:
- Nasdaq ITCH 5.0, includes BX and PSX
- BATS PITCH, includes BYX, BZX, EDGA, and EDGX
- CTA and UTP, includes CQS, CTS, UQDF, UTDF

The input feed is in pcap format, thus in each parser's directory, there is a bash file to convert it to the binary file for parsers to read.

Then each parser outputs an exchange-independent transactions text file. In this file, orders are categorized into four types: Add, Cancel, Replace, Trade. The first column is the type of transaction ('A', 'C', 'R', 'T'), the second column is the timestamp in 10 ms. The third column is the order ID.