import tello
from tello_control_ui_aruco import TelloUI
from time import sleep
import threading
import sys
from socket import *

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
        print(m)
#        send("{0},{1},{2},{3}".format(m[0], int(m[1][0][0]*1000), int(m[1][0][1]*1000), int(m[1][0][2]*1000)))
        send("{0},{1},{2},{3}".format(m[0], int(m[1][0][0]*100), int(m[1][0][1]*100), int(m[1][0][2]*100)))        # 20191018


if __name__ == "__main__":
    # launch tello
    drone = tello.Tello('', 8889)
    telloui = TelloUI(drone, "./img/")
    telloui.marker_detected = marker_detected

    for_debug = False
    if for_debug:
        # for debug
        drone.send_command('command')
        print('sent: command')
        drone.send_command('streamon')
        print('sent: streamon')

    telloui.root.mainloop()
