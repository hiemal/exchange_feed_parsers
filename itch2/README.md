# ITCH 2
###### Kael @ Domeyard. 2016 Winter.
zizhang _dot_ hu _at_ sloan _dot_ mit _dot_ edu

## Introduction
This is a better project to build orderbook, analyze anomalies, and visualize data than the previous version of itch. 
Since I basiclly refactor the whole project, it may be better to separate this to a brand new project: ITCH 2.

## Build
Put script into the folder where data is. Run `python main.py sl1 sl2 sl3 ...` where sl1, sl2, and sl3 are stocklocates you wanna build, i.e., 2075 for DX on 20150318.
This will give you the csv format transactions. 

To convert it to an exchange-independent format, run `python convert_to_general_format.py`. This will give you a txt file under the same directory. On default this commend is executed automaticly when you execute main function.

## Stocklocate lookup
To lookup stocklocate numbers for target stocks, run `python stocklocate_lookup.py DX DIA ... ` where DX and DIA are just two examples of tickers you wanna lookup.
The program should return something like this `{'DIA': 1904, 'DX': 2075}`. Then you can use these stocklocates to build the transactions.

## Tech Specs
The parser is based on this [documentation](http://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/NQTVITCHspecification.pdf).


## Support
- Nasdaq
- BX
- PSX