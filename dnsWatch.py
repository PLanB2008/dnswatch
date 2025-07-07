#!/usr/bin/env python3

###################################
# by lukas.spitznagel@netzint.de
# Version 1.0 from 25.02.2022
# by andreas.till@netzint.de
# Version 1.1 from 18.05.2022
# by andreas.till@team-till.de
# Version 1.2 from 01.07.2025
#
# needs:
# pip3 install dnspython
#
###################################

import argparse
from dns import resolver
from sys import platform
import time
import os


def sendNotification(text, title):
    if platform == "linux" or platform == "linux2":
        string = "notify-send '" + title + "' '" + text + "'"
    if platform == "darwin":
        # determine linksafe path of mac-notify-send :)
        file_path = os.path.realpath(__file__)
        file_path = os.path.dirname(file_path)
        string = file_path+"/mac-notify-send '" + title + "' '" + text + "'"
    os.system(string.encode("utf-8"))

def checkEntry(dns, expected_address):
    res = resolver.Resolver()
    res.nameservers = ['1.1.1.1']

    try:
        # Try resolving CNAME first
        cname_records = res.resolve(dns, 'CNAME')
        for rdata in cname_records:
            cname_target = str(rdata.target).rstrip('.')
            print("CNAME:", cname_target)

            if expected_address:
                expected_clean = expected_address.rstrip('.')
                # Loose match: exact OR endswith
                if cname_target == expected_clean or cname_target.endswith("." + expected_clean):
                    # Success! Now resolve A records for bonus
                    a_records = res.resolve(cname_target, 'A')
                    for a in a_records:
                        print("A (via CNAME):", a.address)
                    return cname_target
                else:
                    return False
            return cname_target

    except resolver.NoAnswer:
        pass  # No CNAME, fall back to A

    except Exception as e:
        print("CNAME resolution failed:", str(e))

    try:
        a_records = res.resolve(dns, 'A')
        for rdata in a_records:
            print("A:", rdata.address)
            if expected_address and rdata.address != expected_address:
                return False
            return rdata.address
    except Exception as e:
        print("A record resolution failed:", str(e))
        return False

    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dns", required = True, help = "DNS name to check")
    parser.add_argument("-a", "--address", required = False, help = "Expected address for dns entry")
    args = parser.parse_args()

    if not args.address:
        args.address = ''
    remember = 0

    print("DNSWatcher has started for " + args.dns + " -> " + args.address)

    try:
        while True:
            check = checkEntry(args.dns, args.address)
            if check:
                sendNotification("Entry is now set correctly!\n" + args.dns + " -> " + check, "👨🏻‍💻 DNS Watcher")
                print("Entry is now set correctly!\n" + args.dns + " -> " + check , "👨🏻‍💻 DNS Watcher")
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
