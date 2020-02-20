#!/usr/bin/python
# -*- coding: utf-8 -*-

from camera import AmscopeCamera, WebCamera

import time

class AbstractCameraSettings():
    def __init__(self, camera, device):
        raise NotImplementedError

class WebCameraSettings(AbstractCameraSettings):
    def __init__(self, camera):

        self.camera = camera
        #self.settingsFuncs = [self.setBrightness, self.setContrast,
        #                    self.setExposure, self.setRotation, self.setGain]


class AmscopeCameraSettings(AbstractCameraSettings):
    def __init__(self, camera, device):
        self.camera = camera
        self.deviceId = device
        self.serial = self.initDeviceSerial()
        self.settingsFuncs = [self.setBrightness, self.setContrast,
                            self.setExposure, self.setRotation, self.setGain]
        self.setFixedSize(self.size())

    def initDeviceSerial(self):
        self.camera.activate()
        serial = str(self.camera.capture.get_serial())
        self.camera.deactivate()
        return serial
