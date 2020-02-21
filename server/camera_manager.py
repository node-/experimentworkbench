#!/usr/bin/python

import asyncio
import cv2
#import yaml

from base64 import b64encode
from camera import WebCamera, AmscopeCamera

class CameraManager():
    devices = []
    cameras = {}
    frames = {}
    frames_jpg = {}
    _frame = None
    # startup devices
    #new_devices = [{'name' : "test", 'id' : 0, 'type': 'amscope'}]
    new_devices = [{'name' : "test", 'id' : 0, 'type': 'webcam'}]

    def __init__(self):
        """
        with open(yml_cfg, 'r') as stream:
            try:
                print(yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                print(exc)
        """
        pass

    def has_frame(self):
        return type(self._frame) != None

    def add_device(self, d):
        print("Adding device: %s" % d)
        Camera = AmscopeCamera if d['type'] == "amscope" else WebCamera
        self.cameras[d['id']] = Camera(name=d['name'], device=int(d['id']))
        self.devices.append(d)
        self.frames_jpg[d['id']] = None
        print(self.frames_jpg)

    def deactivate_all_cams_except(self, camera):
        for v in self.cameras.values():
            if camera != v:
                if v.is_active:
                    v.deactivate()

    def apply_settings(self, d, camera):
        pass

    def pull_image(self, d, camera):
        self._frame = camera.get_frame()

        if not self.has_frame():
            print("no frame!")
            return

        self.frames[d['id']] = self._frame
        self.frames_jpg[d['id']] = cv2.imencode('.png', self._frame)[1].tobytes()
    
    def loop(self):
        # add pending new devices
        while self.new_devices:
            self.add_device(self.new_devices.pop())

        self._frame = None
        for d in self.devices:
            camera = self.cameras[d['id']]           
            self.deactivate_all_cams_except(camera)
            camera.activate()
            self.apply_settings(d, camera)
            self.pull_image(d, camera)

            #print(self._frame)
            # apply settings


    



