#!/usr/bin/env python
# Name:     isthisipbad.py
# Purpose:  Checka IP against popular IP blacklist
# By:       Jerry Gamblin
# Date:     10.05.15
# Modified  10.05.15
# Rev Level 0.1
# -----------------------------------------------

import os
import sys
import json
import urllib
import urllib2
import hashlib
import argparse
import re
import socket
import dns.resolver
from urllib2 import urlopen


def color(text, color_code):
    if sys.platform == "win32" and os.getenv("TERM") != "xterm":
        return text

    return '\x1b[%dm%s\x1b[0m' % (color_code, text)


def red(text):
    return color(text, 31)


def blink(text):
    return color(text, 5)


def green(text):
    return color(text, 32)


def blue(text):
    return color(text, 34)


def content_test(url, badip):
    """ 
    Test the content of url's response to see if it contains badip.

        Args:
            url -- the URL to request data from
            badip -- the IP address in question

        Returns:
            Boolean
    """

    try:
        request = urllib2.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36')
        html_content = urllib2.build_opener().open(request).read()

        matches = re.findall(badip, html_content)

        return len(matches) == 0
    except Exception, e:
        print "Error! %s" % e
        return False

bls = ["zen.spamhaus.org", "spam.abuse.ch", "cbl.abuseat.org", "virbl.dnsbl.bit.nl", "dnsbl.inps.de", 
    "ix.dnsbl.manitu.net", "dnsbl.sorbs.net", "bl.spamcannibal.org", "bl.spamcop.net", 
    "xbl.spamhaus.org", "pbl.spamhaus.org", "dnsbl-1.uceprotect.net", "dnsbl-2.uceprotect.net", 
    "dnsbl-3.uceprotect.net", "db.wpbl.info"]

URLS = [
    #TOR
    ('http://torstatus.blutmagie.de/ip_list_exit.php/Tor_ip_list_EXIT.csv',
     'is not a TOR Exit Node',
     'is a TOR Exit Node',
     False),

    #EmergingThreats
    ('http://rules.emergingthreats.net/blockrules/compromised-ips.txt',
     'is not listed on EmergingThreats',
     'is listed on EmergingThreats',
     True),

    #AlienVault
    ('http://reputation.alienvault.com/reputation.data',
     'is not listed on AlienVault',
     'is listed on AlienVault',
     True),

    #BlocklistDE
    ('http://www.blocklist.de/lists/bruteforcelogin.txt',
     'is not listed on BlocklistDE',
     'is listed on BlocklistDE',
     True),

    #Dragon Research Group - SSH
    ('http://dragonresearchgroup.org/insight/sshpwauth.txt',
     'is not listed on Dragon Research Group - SSH',
     'is listed on Dragon Research Group - SSH',
     True),

    #Dragon Research Group - VNC
    ('http://dragonresearchgroup.org/insight/vncprobe.txt',
     'is not listed on Dragon Research Group - VNC',
     'is listed on Dragon Research Group - VNC',
     True),

    #OpenBLock
    ('http://www.openbl.org/lists/date_all.txt',
     'is not listed on OpenBlock',
     'is listed on OpenBlock',
     True),

    #NoThinkMalware
    ('http://www.nothink.org/blacklist/blacklist_malware_http.txt',
     'is not listed on NoThink Malware',
     'is listed on NoThink Malware',
     True),
     
    #NoThinkSSH
    ('http://www.nothink.org/blacklist/blacklist_ssh_all.txt',
     'is not listed on NoThink SSH',
     'is listed on NoThink SSH',
     True),

    #Feodo
    ('http://rules.emergingthreats.net/blockrules/compromised-ips.txt',
     'is not listed on Feodo',
     'is listed on Feodo',
     True),

    #antispam.imp.ch
    ('http://antispam.imp.ch/spamlist',
     'is not listed on antispam.imp.ch',
     'is listed on antispam.imp.ch',
     True),

    #dshield
    ('http://www.dshield.org/ipsascii.html',
     'is not listed on dshield',
     'is listed on dshield',
     True),

    #malc0de
    ('http://malc0de.com/bl/IP_Blacklist.txt',
     'is not listed on malc0de',
     'is listed on malc0de',
     True),

    #MalWareBytes
    ('http://hosts-file.net/rss.asp',
     'is not listed on MalWareBytes',
     'is listed on MalWareBytes',
     True)]


if __name__ == "__main__":

    my_ip = urlopen('http://ip.42.pl/raw').read()

    print(blue('Check IP addresses against popular IP blacklist'))
    print(blue('A quick and dirty script by @jgamblin and @lojikil'))
    print('\n')
    print(red('Your public IP address is {0}'.format(my_ip)))
    print('\n')

    #Get IP To SCAN

    resp = raw_input('Would you like to check {0}? (Y/N):'.format(my_ip))

    if resp.lower() in ["yes", "y"]:
        badip = my_ip
    else:
        badip = raw_input(blue("What IP would you like to check?: "))

    print('\n')

    #IP INFO
    reversed_dns = socket.getfqdn(badip)
    geoip = urllib.urlopen('http://api.hackertarget.com/geoip/?q=' + badip).read()

    print(blue('The FQDN for {0} is {1}'.format(badip, reversed_dns)))
    print('\n')
    print(red('Some GEOIP Information:'))
    print(blue(geoip))
    print('\n')


    BAD = 0
    GOOD = 0

    for url, succ, fail, mal in URLS:
        if content_test(url, badip):
            print(green('{0} {1}'.format(badip, succ)))
            GOOD += 1
        else:
            if mal:
                BAD += 1

            print(red('{0} {1}'.format(badip, fail)))

   
    for bl in bls:
        try:
            my_resolver = dns.resolver.Resolver()
            query = '.'.join(reversed(str(badip).split("."))) + "." + bl
            answers = my_resolver.query(query, "A")
            print (red(badip + ' is listed on ' + bl))
            BAD += 1
        except dns.resolver.NXDOMAIN: 
            print (green(badip + ' is not listed on ' + bl))
            GOOD += 1
            
#This Doesnt work because I am stupid. 
#print('\n')
#print(red('{0} is on {1}/{2} lists.'.format(badip, BAD, GOOD)))