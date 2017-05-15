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

while(True):

    os.system("hciconfig hci0 down")
    os.system("hciconfig hci0 up")

    scan_content = pexpect.spawn("timeout 5s hcitool lescan").read()
    print scan_content
    
    for content in scan_content.splitlines():
        match_id = re.match(r'([0-9A-F]{2}[:-]){5}([0-9A-F]{2})', content, re.M)
        if match_id:
            address = match_id.group()        
            print 'address ' + address
            if address not in current_devices:                        
                battery_info = None
                uid_value = None
                try:
                    battery_info = pexpect.spawn("timeout 5s gatttool -t random -b "+ address +" --char-read --handle 0x0015")
                    if battery_info:
                        battery_info = battery_info.read()
                        if len(battery_info) == 0:
                            print "Can't read battery so this is not samrt locker"
                            continue
                    else:
                        battery_info = None
 
                    interactive = pexpect.spawn("gatttool -t random -b " + address + " -I")
                    interactive.expect(r"\[LE\]>", timeout=3)
                    interactive.sendline("connect")
                    interactive.expect(["Connection successful"], timeout=10)
                    interactive.expect(r"\[LE\]>", timeout=10)               
                    interactive.sendline("char-write-req 0x000c 0100")
                    interactive.expect("Characteristic value was written successfully")
                    interactive.sendline("char-write-req 0x000e 0500b0000010 -listen")
                    interactive.expect("Characteristic value was written successfully")
                    interactive.expect("Notification handle = 0x000b value: ([a-z0-9]{2}[ ]){18}", timeout=10)
                    uid_info = interactive.after
                    uid_value = re.search(r'([a-z0-9]{2}[ ]){18}', uid_info, re.M).group()
                    print "uid " + uid_value
                except:
                    print "error"
                else:            
                    if battery_info:
                        battery_value = re.match('Characteristic value/descriptor: (.*)', battery_info).groups()[0]
                        if battery_value:
                            print "battery info: " + str(int(battery_value, 16))
                            
                            current_devices.append(address)
                            battery.append(str(int(battery_value, 16)))
                            mac_address.append(address)
                            id.append(uid_value[12:35])
                        else:
                            pass
    
    
    print mac_address
    print id
    print battery
    if sorted(current_devices) != sorted(last_devices):
        request_data = []        
        for index, address in enumerate(mac_address):
            request_data.append({"csn": id[index], "mac":address, "battery":battery[index] })        
        print 'post' + json.dumps(request_data)
        r = requests.post("http://dev_bike.infinitas.tech/station_v1/resp_locks", data=json.dumps(request_data))
        print r.text
        last_devices = current_devices
    else:
        print "current devices == last devices so not post"
    current_devices = []
    mac_address = []
    id = []
    battery = []
                

