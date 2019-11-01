import tello
from tello_control_ui_aruco import TelloUI
from time import sleep
import threading
import sys
from socket import *
import pprint

drone = False
telloui = False

addr = (gethostbyname("localhost"), 65008)
sock = socket(AF_INET, SOCK_DGRAM)


def send(str):
    sock.sendto((str + ';').encode('utf-8'), addr)
    print("sent: " + str)


def marker_detected(markers):
    print(markers)
    for m in markers:
#        pprint.pprint(m) # pitch yaw roll
        send("{0},{1},{2},{3},{4},{5},{6}".format(m[0], 
            m[1][0], m[1][1], m[1][2], # tvec
            m[2][0], m[2][1], m[2][2]  # pitch yaw roll
            )) 


if __name__ == "__main__":
    # launch tello
    drone = tello.Tello('', 8889)
    telloui = TelloUI(drone, "./img/")
    telloui.marker_detected = marker_detected

    if len(sys.argv) >= 2 and sys.argv[1] == 'debug':
        print("debugging...")
        for_debug = True
        drone.for_debug = for_debug
    else:
        for_debug = False

    if for_debug:
        sleep(2)
        # for debug
        drone.send_command('command')
        print('sent: command')
        drone.send_command('streamon')
        print('sent: streamon')

    telloui.root.mainloop()
