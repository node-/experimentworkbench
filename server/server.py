#!/usr/bin/env python

import flask
from flask import render_template, send_from_directory, Response, request
#import connexion
#import camera_controller

import Amscope
from camera import WebCamera, AmscopeCamera
import os
import time
import cv2

# Create the application instance
#app = connexion.App(__name__, specification_dir='./')

app = flask.Flask(__name__)

# Read the swagger.yml file to configure the endpoints
#app.add_api('swagger.yml')


"""
@app.route("/")
def home():
    return render_template('index.html')


@app.route('/<path:path>')
def send_root(path):
    return send_from_directory('templates', path)
"""

def gen(camera):
    # safely switch between active camera and stream 
    camera.activate()
    while True:
        frame = camera.get_frame()
        frame = cv2.imencode('.jpg', frame)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    camera.deactivate()


@app.route('/webcam/<deviceid>')
def webcam_feed(deviceid):
    name = request.args.get('name')
    if not name:
        name = deviceid
    return Response(gen(WebCamera(int(deviceid), name)),
                mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/amscope/<deviceid>')
def amscope_feed(deviceid):
    name = request.args.get('name')
    if not name:
        name = deviceid
    return Response(gen(AmscopeCamera(int(deviceid), name)),
                mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)

