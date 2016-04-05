#!/bin/bash

find . -maxdepth 1 -name "*.pcap" | xargs -I {} -P4 sh -c 'tshark -r {} -T fields -e data | cut -c 41- | xxd -r -p > `basename {} .pcap`.bin'
