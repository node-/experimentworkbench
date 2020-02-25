#!/usr/bin/python

import asyncio

# monkey patch for timer coroutines
import nest_asyncio
nest_asyncio.apply()

from aiohttp import web
from aiojobs.aiohttp import atomic
import aiohttp_cors
import socketio
import json
import time

from camera_manager import CameraManager, amscope_settings_range

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
    return web.Response(text="yo", content_type='text/html')

async def set_config(request):
    mgmt.config.set(await request.json())
    return web.Response()

async def add_device(request):
    mgmt.new_devices.append(await request.json())
    return web.Response()

async def get_frame(request):
    try:
        device_id = int(request.match_info.get('id', '0'))
        return web.Response(body=mgmt.frames_jpg[device_id], content_type='image/png')
    except Exception as e:
        return web.Response(body=str(e))

async def get_device_settings(request):
    try:
        device_id = int(request.match_info.get('id', '0'))
        return web.Response(body=json.dumps(mgmt.cameras[device_id].settings), content_type='application/json')
    except Exception as e:
        return web.Response(body=str(e))

async def set_device(request):
    try:
        device_id = int(request.match_info.get('id', '0'))
        mgmt.set_device(device_id, await request.json())
        return web.Response()
    except Exception as e:
        return web.Response(body=str(e))

async def manage_cameras():
    count = 0
    while True:
        await mgmt.loop()
        await sio.emit('device_update', {'devices': mgmt.devices})
        await sio.emit('device_settings', {'settings': mgmt.get_all_camera_settings()})
        #await sio.emit('response', {'data': 'Server Heartbeat: %d' % count})
        if mgmt.has_frame():
            await sio.emit('frame', {'data' : None, 'update' : True})
        if len(mgmt.errors):
            await sio.emit('error', {'error' : mgmt.errors})
        await sio.sleep(1)
        count += 1


cors.add(app.router.add_post('/config', set_config))
cors.add(app.router.add_post('/add_device', add_device))
cors.add(app.router.add_post('/set_device/{id}', set_device))
app.router.add_get('/', index)
app.router.add_get('/frame/{id}', get_frame)
app.router.add_get('/settings/{id}', get_device_settings)

async def main():
    sio.start_background_task(manage_cameras)
    web.run_app(app, port=3005)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


