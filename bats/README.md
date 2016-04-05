# BAT Parser
###### Kael @ Domeyard. 2016 Winter.
zizhang _dot_ hu _at_ sloan _dot_ mit _dot_ edu


## Things need to notice

Time offset is the nanosecond offset from _last_ unit timestamp.

Since PITCH does not contain stock locate number to match those modify orders with a specific stock, this program is ridiculously slow. 

In PITCH, those modify orders can only work on add orders, namely, there is no modify on modify.

## Build
Put scripts into directory that contains data, and then run `python main.py ticker1 ticker2 ticker3 ...` where tickers are those you concern, i.e., 'DX'.

The output is an exchange independent format, 'ticker.txt'.

## Reference
The parser part is enhanced based on [github/klon](https://github.com/klon/bats-pitch-parser). The original parser is not
able to use on the latest version of data, and is severely lack functionality.


## Support
The parser supports BYX, BZX, EDGA, and EDGX. For details, please refer to PITCH technical [documentation](http://cdn.batstrading.com/resources/membership/BATS_US_EQUITIES_OPTIONS_MULTICAST_PITCH_SPECIFICATION.pdf) and EDGE technical documentation(in /docs).

The only difference between out version of EDGE (before it was acquared by BATS) is that the old version of EDGE uses 8 bytes timestamp which marks the time since epoch, while BATS uses seconds since midnight.