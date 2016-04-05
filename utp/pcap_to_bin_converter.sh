#!/bin/bash

find . -maxdepth 1 -name "*.pcap" | xargs -I {} -P4 sh -c 'tshark -r {} -T fields -e data | xxd -r -p > `basename {} .pcap`.bin'