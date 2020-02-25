#!/usr/bin/python

import asyncio

# monkey patch for timer coroutines
import nest_asyncio
nest_asyncio.apply()

import cv2
import os
import time
from datetime import datetime
from camera import *

#import yaml
#from base64 import b64encodea import WebCamera, AmscopeCamera

amscope_settings_range = {
    "exposure" : (400, 2000000),
    "gain" : (100, 300),
    "temp" : (2000, 15000),
    "tint" : (200, 2500),
    "rotation" : (0, 360)
}

class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback()

    def cancel(self):
        self._task.cancel()

class GlobalConfig():
    default = {
        "outputPath" : r"C:\Users\kosberg\code\experimentworkbench\test",
        "intervalTime" : 10,
        "timelapseEnabled": True
    }

    settings = default
    def __init__(self, database):
        pass

    def set(self, new):
        print(new)
        self.settings = new


# temporary helper functions
def get_amscope_settings(camera):
    camera.activate()
    temp, tint = camera.capture.get_temperature_tint()
    settings = {
        "exposure" : camera.capture.get_exposure_time(),
        "gain" : camera.capture.get_exposure_gain(),
        "temp" : temp,
        "tint" : tint,
        "rotation" : 0,
        "serial" : camera.capture.get_serial()
    }
    return settings


def get_date_string():
    return time.strftime("%Y-%m-%d_%H-%M-%S")

def create_path_if_not_exist(path):
    if not os.path.exists(path):
        os.makedirs(path)


class CameraManager():
    config = GlobalConfig("test")
    devices = []
    cameras = {}
    frames = {}
    frames_jpg = {}
    errors = []
    _frame = None
    _has_snapped = False
    _should_snap = False
    _time_last_snap = datetime.now()
    _timer = None

    # startup devices
    #new_devices = [{'name' : "test", 'id' : 0, 'type': 'amscope'}]
    new_devices = [
        {'name' : "foo", 'id' : 0, 'type': 'amscope'},
        {'name' : "bar", 'id' : 1, 'type': 'amscope'},
    ]

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
        c = Camera(name=d['name'], device=int(d['id']))
        self.cameras[d['id']] = c
        self.devices.append(d)
        self.frames_jpg[d['id']] = None

        assert(Camera == AmscopeCamera)
        c.settings = get_amscope_settings(c)
        print(c.settings)
        if not c.is_active:
            return False

    def set_device(self, device_id, settings):
        print(settings)
        self.cameras[device_id].settings = settings

    def deactivate_all_cams_except(self, camera):
        for v in self.cameras.values():
            if camera != v and v.is_active:
                v.deactivate()

    def apply_settings(self, camera):
        camera.set_temp_tint(
            camera.settings["temp"],
            camera.settings["tint"]
        )

        camera.set_exposure(camera.settings["exposure"])
        camera.set_gain(camera.settings["gain"])
        camera.set_rotation(camera.settings["rotation"])

    def pull_image(self, d, camera):
        self._frame = None
        self._frame = camera.get_frame()

        if not self.has_frame():
            print("no frame!")
            return

        self.frames[d['id']] = self._frame
        self.frames_jpg[d['id']] = cv2.imencode('.png', self._frame)[1].tobytes()
    
    """
    def should_snap(self):
        if self.time_to_snap and not self._has_snapped:
            self._has_snapped = False
            return True
        return False
    """

    def get_output_path(self, device):
        outpath = os.path.join(
            self.config.settings["outputPath"], 
            device['name']
        )
        print(outpath)
        create_path_if_not_exist(outpath)
        return os.path.join(outpath, get_date_string() + ".png")

    def start_timelapse_timer(self):
        if self._timer:
            return
        self._should_snap = True

        async def timer_cb(self):
            self._should_snap = True
            self._timer = None

        self._timer = Timer(
            self.config.settings["intervalTime"], 
            lambda: timer_cb(self)
        )

    async def loop(self):
        if self.config.settings["timelapseEnabled"]:
            self.start_timelapse_timer()
        else:
            self._timer.cancel()
            self._timer = None

        self.errors = []
        # add pending new devices
        while self.new_devices:
            if not self.add_device(d := self.new_devices.pop()):
                self.errors.append(d['id'])
        
        # freeze _should_snap incase it changes while looping thru devices
        should_snap = self._should_snap
        
        for d in self.devices:
            camera = self.cameras[d['id']]           
            self.deactivate_all_cams_except(camera)
            camera.activate()
            self.apply_settings(camera)
            await asyncio.sleep(1)
            self.pull_image(d, camera)
            if should_snap:
                cv2.imwrite(self.get_output_path(d), self._frame)

        if should_snap:
            self._should_snap = False






    



