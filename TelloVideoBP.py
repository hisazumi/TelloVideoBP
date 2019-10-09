import tello
from tello_control_ui_aruco import TelloUI
from time import sleep
import threading
import sys

drone = False
telloui = False
commands = []
all_detected_ids = set()


def marker_detected(ids):
    global all_detected_ids
    print(ids)
    all_detected_ids |= set(ids)
    print(all_detected_ids)


if __name__ == "__main__":
    # launch tello
    drone = tello.Tello('', 8889)
    telloui = TelloUI(drone, "./img/")
    telloui.marker_detected = marker_detected

    # for debug
    drone.send_command('command')
    print('sent: command')
    drone.send_command('streamon')
    print('sent: streamon')

    telloui.root.mainloop()
