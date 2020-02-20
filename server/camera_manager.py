
import asyncio
from camera import WebCamera

class CameraManager():
    devices = []
    cameras = {}
    frames = {}
    new_devices = []

    def __init__(self):
        pass

    def loop(self):
        # add devices
        while self.new_devices:
            d = self.new_devices.pop()
            print("Adding device: %s" % d)
            self.cameras[d['id']] = WebCamera(d['id'], d['name'])
            self.devices.append(d)


        # apply settings, pull images
        for c in self.devices:
            #print(c['name'])
            #pass
            self.frame[self.cameras[c['id']]] = self.cameras[c['id']].get_frame()





        