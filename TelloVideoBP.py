import threading
from . protocol import *

# https://github.com/hanyazou/TelloPy/blob/develop-0.7.0/tellopy/_internal/tello.py


class VideoData(object):
    packets_per_frame = 0

    def __init__(self, data):
        self.h0 = byte(data[0])
        self.h1 = byte(data[1])
        if VideoData.packets_per_frame < (self.h1 & 0x7f):
            VideoData.packets_per_frame = (self.h1 & 0x7f)

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
    def __init__(self, drone):
        self.drone = drone
        self.log = drone.log
        self.cond = threading.Condition()
        self.queue = []
        self.closed = False
        self.prev_video_data = None
        self.wait_first_packet_in_frame = True
        self.ignore_packets = 0
        self.name = 'VideoStream'
        drone.subscribe(drone.EVENT_CONNECTED, self.__handle_event)
        drone.subscribe(drone.EVENT_DISCONNECTED, self.__handle_event)
        drone.subscribe(drone.EVENT_VIDEO_DATA, self.__handle_event)

    def read(self, size):
        self.cond.acquire()
        try:
            if len(self.queue) == 0 and not self.closed:
                self.cond.wait(5.0)
            data = bytes()
            while 0 < len(self.queue) and len(data) + len(self.queue[0]) < size:
                data = data + self.queue[0]
                del self.queue[0]
        finally:
            self.cond.release()
        # returning data of zero length indicates end of stream
        self.log.debug('%s.read(size=%d) = %d' % (self.name, size, len(data)))
        return data

    def seek(self, offset, whence):
        self.log.info('%s.seek(%d, %d)' % (str(self.name), offset, whence))
        return -1

    def __handle_event(self, event, sender, data):
        if event is self.drone.EVENT_CONNECTED:
            self.log.info('%s.handle_event(CONNECTED)' % (self.name))
        elif event is self.drone.EVENT_DISCONNECTED:
            self.log.info('%s.handle_event(DISCONNECTED)' % (self.name))
            self.cond.acquire()
            self.queue = []
            self.closed = True
            self.cond.notifyAll()
            self.cond.release()
        elif event is self.drone.EVENT_VIDEO_DATA:
            self.log.debug('%s.handle_event(VIDEO_DATA, size=%d)' %
                           (self.name, len(data)))
            video_data = VideoData(data)
            if 0 < video_data.gap(self.prev_video_data):
                self.wait_first_packet_in_frame = True

            self.prev_video_data = video_data
            if self.wait_first_packet_in_frame and byte(data[1]) != 0:
                self.ignore_packets += 1
                return
            if self.wait_first_packet_in_frame:
                self.log.debug('%s.handle_event(VIDEO_DATA): ignore %d packets' %
                               (self.name, self.ignore_packets))
            self.ignore_packets = 0
            self.wait_first_packet_in_frame = False

            self.cond.acquire()
            self.queue.append(data[2:])
            self.cond.notifyAll()
            self.cond.release()
