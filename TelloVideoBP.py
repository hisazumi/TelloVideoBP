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


def marker_detected(ids):
    print(ids)
    for id in ids:
        send(str(id))


if __name__ == "__main__":
    # launch tello
    drone = tello.Tello('', 8889)
    telloui = TelloUI(drone, "./img/")
    telloui.marker_detected = marker_detected

    for_debug=False

    # for debug
    if for_debug:
        drone.send_command('command')
        print('sent: command')
        drone.send_command('streamon')
        print('sent: streamon')

    telloui.root.mainloop()
