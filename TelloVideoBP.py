import socket
import sys
import time

import av
import cv2.cv2 as cv2  # for avoidance of pylint error
import numpy as np

# https://github.com/hanyazou/TelloPy/blob/develop-0.7.0/tellopy/_internal/tello.py

class VideoData(object):
    packets_per_frame = 0

    def __init__(self, data):
        self.h0 = VideoData.byte(data[0])
        self.h1 = VideoData.byte(data[1])
        if VideoData.packets_per_frame < (self.h1 & 0x7f):
            VideoData.packets_per_frame = (self.h1 & 0x7f)

    @classmethod
    def byte(_, c):
        if isinstance(c, str):
            return ord(c)
        return c

    def gap(self, video_data):
        if video_data is None:
            return 0

        v0 = self
        v1 = video_data

        loss = 0
        if ((v0.h0 != v1.h0 and v0.h0 != ((v1.h0 + 1) & 0xff))
            or (v0.h0 != v1.h0 and (v0.h1 & 0x7f) != 00)
                or (v0.h0 == v1.h0 and (v0.h1 & 0x7f) != (v1.h1 & 0x7f) + 1)):
            loss = v0.h0 - v1.h0
            if loss < 0:
                loss = loss + 256
            loss = loss * VideoData.packets_per_frame + \
                ((v0.h1 & 0x7f) - (v1.h1 & 0x7f) - 1)

        return loss

class VideoStream(object):
    def __init__(self):
#        self.drone = drone
#        self.log = drone.log
#        self.cond = threading.Condition()
        self.queue = []
        self.closed = False
        self.prev_video_data = None
        self.wait_first_packet_in_frame = True
        self.ignore_packets = 0
#        self.name = 'VideoStream'
        self.udpsize = 2000


    def open(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port = 11111
        self.sock.bind(('', self.port))
        self.sock.settimeout(1.0)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 512 * 1024)

    def read(self, size):
        data = bytes()
        while len(data) < size:
            data = data + self.recv()
        return data

    def seek(self, offset, whence):
        #self.log.info('%s.seek(%d, %d)' % (str(self.name), offset, whence))
        return -1

    def recv(self):
        while True:
            try:
                data, _ = self.sock.recvfrom(self.udpsize)
            except KeyboardInterrupt:
                return
            except socket.timeout:
                print('video recv: timeout')
                # self.start_video()
                data = None
                continue

            print('VIDEO_DATA, size=%d)' % len(data))
            video_data = VideoData(data)
            self.prev_video_data = video_data
            if 0 < video_data.gap(self.prev_video_data):
                continue

            return data[2:]


def for_debug():
    tello_address = ('192.168.10.1', 8889)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
    sock.bind(('', 8889))

    def recv():
        rcvd, _ = sock.recvfrom(3000)
        print('received: ' + str(rcvd))
        return rcvd

    # to receive video -- send cmd: command, streamon
    sock.sendto(b'command', tello_address)
    print ('sent: command')
    recv()

    sock.sendto(b'streamon', tello_address)
    print ('sent: streamon')
    recv()


def main():
    for_debug()

    vs = VideoStream()
    vs.open()

    container = av.open(vs)
    frame_skip = 300

    __dictionary_name = cv2.aruco.DICT_7X7_100
    __dictionary = cv2.aruco.getPredefinedDictionary(__dictionary_name)

    preids_list = []
    preids = set([])    # set variable
    preids2 = set([])   # set
    preids = set(preids_list)

    try:
        while True:
            for frame in container.decode(video=0):
                if 0 < frame_skip:
                    frame_skip = frame_skip - 1
                    continue

                corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(np.array(frame.to_image()), __dictionary)
                start_time = time.time()	# elapsed time(second) from 1970/1/1 00:00;00
                image = cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)
                image = cv2.aruco.drawDetectedMarkers(np.array(image), corners, ids)
                # print('detect marker=',ids)
                i = 0
                if isinstance(ids, np.ndarray) == True:
                    for elem in ids:
                        preids_list = list(ids[i])
                        value = preids_list[0]
                        preids.add(value)
                        i = i + 1
                    print('Detected ArMark ID=', preids)
                    preids2 = preids
                # 読み込んだ画像の高さと幅を取得
                height = int(image.shape[0])
                width = int(image.shape[1])
                resized_img = cv2.resize(image,(width,height))
            cv2.imshow('Original', resized_img)
            cv2.waitKey(1)
            frame_skip = int((time.time() - start_time)/frame.time_base) * 2
    except Exception as ex:
        print('main' + ex)
    finally:
        cv2.destroyAllWindows()


main()
