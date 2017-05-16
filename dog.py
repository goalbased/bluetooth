import requests
import bluetooth
import time
import pexpect
import os, sys, subprocess, shlex, re, json


last_devices = []
current_devices = []
mac_address = []
id = []
battery = []
os.system("hciconfig hci0 down")
os.system("hciconfig hci0 up")
os.system("timeout 5s hcitool lescan --duplicates")


id = "F3:7B:41:01:76:90"
id = id.replace(":", " ")
while(True):
    print 0
    scan_content = pexpect.spawn("timeout 5s hcidump --raw").read()
    s = scan_content.replace("\r", "")
    s = s.replace("\n", "")
    s = s.replace(">", "")
    s = s.replace("   ", " ")
    s= s.replace("  ", " ")
    a = s.index(id)
    print '-'
    print s[a-6:a]
    print '-'
#    print s
    print 1
