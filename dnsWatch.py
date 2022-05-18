#!/usr/bin/env python3

###################################
# by lukas.spitznagel@netzint.de
# Version 1.0 from 25.02.2022
# by andreas.till@netzint.de
# Version 1.1 from 18.05.2022
# needs:
# pip3 install dnspython
#
###################################

import argparse
from dns import resolver
import time
import os

def sendNotification(text, title):
    string = "~/bin/notify-send '" + title + "' '" + text + "'"
    os.system(string.encode("utf-8"))

def checkEntry(dns, address):
    res = resolver.Resolver()
    res.nameservers = ['1.1.1.1']
    try:
        hostnameRecord = res.resolve(dns)
        for rdata in hostnameRecord:
            print (rdata.address)
            hostnameRecord = rdata.address
    except Exception as e:
        print (str(e))
        return False

    if len(address) > 0:
        if hostnameRecord != address:
            return False
     
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dns", required = True, help = "DNS name to check")
    parser.add_argument("-a", "--address", required = False, help = "Expected address for dns entry")
    args = parser.parse_args()

    if not args.address:
        args.address = ''
    remember = 0

    print("Lukas DNSWatcher has started for " + args.dns + " -> " + args.address)

    try:
        while True:
            check = checkEntry(args.dns, args.address)
            if check:
                sendNotification("Entry is now set correctly!\n" + args.dns + " -> " + args.address, "Lukas DNS Watcher")
                print("Entry is now set correctly!\n" + args.dns + " -> " + args.address, "Lukas DNS Watcher")
                remember += 1
                if remember > 5:
                    exit(0)
            else:
                print ('Entry not found yet')
            time.sleep(60)
    except KeyboardInterrupt:
        print("Bye!")


if __name__ == "__main__":
    main()
