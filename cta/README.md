# CTA Parser
###### Kael Hu @ Domeyard, winter 2016
zizhang _dot_ hu _at_ sloan _dot_ mit _dot_ edu

## Tech Specs
For CQS, the parser is based on the elder version of CQS output [spec](https://www.ctaplan.com/publicdocs/ctaplan/notifications/trader-update/cqs%20output%20spec%20v%2059a_042215.pdf) in order to research on historical data on 20150318.

For CTS, I did not found the elder version of documentation. Sorry. The parser is instead based on the latest [version](https://www.nyse.com/publicdocs/ctaplan/notifications/trader-update/cts_output_spec.pdf).

The data before 20150727 for CQS and 20150730 for CTA is using the old header tech spec, which could be found [here](https://ctaplan.com/publicdocs/ctaplan/notifications/announcements/trader-update/6103.pdf).

A sample for the old header is:

```
Message Category = (1) E
Message Type = (1) D
Message Network = (1) E
Retransmission = (2) O
Header Identifier = (1) A
Reserved = (2)
Message Sequence = (9) 000045766
Participant ID = (1) P
Timestamp = (6) 700000

Total (24) bytes
```

If you would like to modify the code to the latest version of CTA, it should be quite easy as most tech specs do not change.

## Build
Run `python main.py ticker1 ticker2 ...` where 'ticker1' is the ticker you need to lookup, i.e., 'F' for Ford. The result will be printed on the screen.


## Todos:
- The file reader currently reads one whole binary file into memory at one time which is ram intensively. Need to fix this. Maybe the previous method that loads msg one by one is better. I have a 16GB ram computer, but some users might not have such big ram.