#!/usr/bin/python

import asyncio
from aiohttp import web
import aiohttp_cors

import socketio

from camera_manager import CameraManager



mgmt = CameraManager()

sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins="*")
app = web.Application()

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
})

sio.attach(app)

@sio.event
async def connect(sid, environ):
    print('Client connected: %s' + str(sid) )
    await sio.emit('response', {'data': 'Connected', 'count': 0}, room=sid)


@sio.event
def disconnect(sid):
    print('Client disconnected: %s' + str(sid) )


async def index(request):
    with open('app.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


async def set_config(request):
    print(await request.read())
    return web.Response()

async def add_device(request):
    mgmt.new_devices.append(await request.json())
    return web.Response()

async def get_frame(request):
    device_id = request.match_info.get('id', '0')
    return web.Response(body=mgmt.frames_jpg[int(device_id)], content_type='image/png')

async def background_task():
    count = 0
    while True:
        mgmt.loop()
        await sio.emit('device_update', {'devices': mgmt.devices})
        await sio.emit('response', {'data': 'Server Heartbeat: %d' % count})
        if mgmt.has_frame():
            await sio.emit('frame', {'data' : None, 'update' : True})
        await sio.sleep(1)
        count += 1

cors.add(app.router.add_post('/config', set_config))
cors.add(app.router.add_post('/add_device', add_device))
app.router.add_get('/', index)
app.router.add_get('/frame/{id}', get_frame)

if __name__ == '__main__':
    sio.start_background_task(background_task)
    web.run_app(app, port=3005)

