#!/usr/bin/python

import asyncio

# monkey patch for timer coroutines
import nest_asyncio
nest_asyncio.apply()

import cv2
import os
import time
import json

from datetime import datetime
from camera import *

#import yaml
#from base64 import b64encodea import WebCamera, AmscopeCamera

CONFIG_JSON = "config.json"

AMSCOPE_SETTINGS_RANGE = {
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
        "outputPath" : "",
        "intervalTime" : 300,
        "timelapseEnabled": False
    }
    json = ""

    settings = default
    _init_done = False

    def __init__(self, db_path):
        self.db_path = db_path
        try:
            with open(self.db_path, "r") as cfg:
                self.json = json.loads(cfg.read())
                self.settings = self.json
                print("Loaded %s " % self.db_path)
        except (IOError, json.decoder.JSONDecodeError) as e:
            print("Error loading config, will overwrite: %s" % e)
            self.json = self.default
        self._init_done = True

    def set_camera_settings(self, settings):
        self.settings["cameras"] = settings
        #self.format_settings_json(settings)

    def save(self):
        if not self._init_done:
            return False
        #self.format_settings_json(self.settings)
        with open(self.db_path, "w+") as cfg:
            #print(self.json)
            #print(json.dumps(self.json, indent=4, sort_keys=True))
            #cfg.write("test")
            cfg.write(json.dumps(self.json, indent=4, sort_keys=True))
            print("Saved config to %s " % self.db_path)


"""
    def format_settings_json(self, settings):
        print(settings)
        print(self.json)
        for camera, params in settings.items():
            for k, v in params.items():
                self.json["cameras"][camera][k] = str(v)

"""

# temporary helper functions
def get_amscope_settings(camera):
    camera.activate()
    temp, tint = camera.capture.get_temperature_tint()
    settings = {
        "id" : camera.device,
        "name" : camera.name,
        "exposure" : camera.capture.get_exposure_time(),
        "gain" : camera.capture.get_exposure_gain(),
        "temp" : temp,
        "tint" : tint,
        "rotation" : 0,
        "serial" : str(camera.capture.get_serial())
    }
    return settings

def get_webcam_settings(camera):
    settings = {
        "exposure" : camera.capture.get(cv2.CAP_PROP_EXPOSURE),
        "gain" : camera.capture.get(cv2.CAP_PROP_GAIN),
        "temp" : False,
        "tint" : False,
        "rotation" : 0,
        "serial" : ""
    }
    return settings


def get_date_string():
    return time.strftime("%Y-%m-%d_%H-%M-%S")

def create_path_if_not_exist(path):
    if not os.path.exists(path):
        os.makedirs(path)


class CameraManager():
    config = GlobalConfig(CONFIG_JSON)
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
        #{'name' : "bar", 'id' : 1, 'type': 'amscope'},
    ]

    def __init__(self):
        pass

    def has_frame(self):
        return type(self._frame) != None

    def get_settings_from_serial(self, serial):
        print(self.config.settings["cameras"])
        for cid, settings in self.config.settings["cameras"].items():
            if not settings:
                return
            if serial in settings["serial"]:
                return self.cameras[int(cid)].settings

    def add_device(self, d):
        print("Adding device: %s" % d)
        Camera = AmscopeCamera if d['type'] == "amscope" else WebCamera
        c = Camera(name=d['name'], device=int(d['id']))
        self.cameras[d['id']] = c
        self.devices.append(d)
        self.frames_jpg[d['id']] = None
        
        assert(Camera == AmscopeCamera)
        c.activate()
        if s := self.get_settings_from_serial(str(c.capture.get_serial())):
            print("Found camera! %s" % s)
            c.settings = s
            print(s)
        else:
            c.settings = get_amscope_settings(c)
        #print(c.settings)
        c.type = "amscope"
        self.apply_settings(c)

        #c.settings = get_webcam_settings(c)


    def set_device(self, device_id, settings):
        self.cameras[device_id].settings = settings

    def get_all_camera_settings(self):
        return {k: v.settings for (k, v) in self.cameras.items()}

    def deactivate_all_cams_except(self, camera):
        for v in self.cameras.values():
            if camera != v and v.is_active:
                v.deactivate()

    def apply_settings(self, camera):
        self.config.set_camera_settings(self.get_all_camera_settings())
        print(camera.settings)
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
            if self._timer:
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
        self.config.save()






    



