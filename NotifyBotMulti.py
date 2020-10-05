import requests
import configparser
import json
import time
from defADSBX import pullADSBX
from defOpenSky import pullOpenSky
from colorama import Fore, Back, Style
import platform
if platform.system() == "Windows":
    from colorama import init
    init(convert=True)
from planeClass import Plane
from datetime import datetime
import pytz
main_config = configparser.ConfigParser()
main_config.read('mainconf.ini')
import os
#Setup Plane Objects off of Plane configs
planes = {}
for filename in os.listdir(os. getcwd()):
    if filename.endswith(".ini") and filename != "mainconf.ini":
        plane_config = configparser.ConfigParser()
        plane_config.read(filename)
        planes[plane_config.get('DATA', 'ICAO').upper()] = Plane(plane_config.get('DATA', 'ICAO'), filename)

running_Count = 0
try:
    tz = pytz.timezone(main_config.get('DATA', 'TZ'))
except pytz.exceptions.UnknownTimeZoneError:
    tz = pytz.UTC

while True:
    datetime_tz = datetime.now(tz)
    if datetime_tz.hour == 0 and datetime_tz.minute == 0:
        running_Count = 0
    running_Count +=1
    start_time = time.time()
    print (Back.GREEN,  Fore.BLACK, "--------", running_Count, "--------", datetime_tz.strftime("%I:%M:%S %p"), "-------------------------------------------------------", Style.RESET_ALL)
    if main_config.get('DATA', 'SOURCE') == "ADSBX":
        data, failed = pullADSBX(planes)
        if failed == False:
            if data['ac'] != None:
                for key, obj in planes.items():
                    has_data = False
                    for planeData in data['ac']:
                        if planeData['icao'] == key:
                            obj.run(planeData)
                            has_data = True
                            break
                    if has_data is False:
                        obj.run(None)
            else:
                for obj in planes.values():
                    obj.run(None)
    elif main_config.get('DATA', 'SOURCE') == "OPENS":
        planeData, failed = pullOpenSky(planes)
        if failed == False:
            if planeData.states != []:
                for key, obj in planes.items():
                    has_data = False
                    for dataState in planeData.states:
                        if (dataState.icao24).upper() == key:
                            obj.run(dataState)
                            has_data = True
                            break
                    if has_data is False:
                        obj.run(None)
            else:
                for obj in planes.values():
                    obj.run(None)
    elapsed_calc_time = time.time() - start_time
    datetime_tz = datetime.now(tz)
    print (Back.GREEN,  Fore.BLACK, "--------", running_Count, "--------", datetime_tz.strftime("%I:%M:%S %p"), "------------------------Elapsed Time-", elapsed_calc_time, " -------------------------------------", Style.RESET_ALL)
    print(Back.RED, "Sleep 30", Style.RESET_ALL)
    time.sleep(30)
