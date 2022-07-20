from dotenv import load_dotenv

from db.tables.Datum import DatumTableSchema
load_dotenv()

from aiohttp import web
import asyncio
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from BTreadDevice import BTreadDevice, BTreadDeviceEvents
from db import manager as dbmanager
from FTMS import FTMSMachineStatusEvent, FTMSMachineStatusEventOptions, FTMSTrainingStatus, FTMSTreadmillData
import socketio
from types import NoneType
from bleak_winrt.windows.devices.bluetooth.advertisement import BluetoothLEAdvertisementFilter, BluetoothLEAdvertisement

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

_scanned_devices = []
_device: BTreadDevice | NoneType = None

adv_filter = BluetoothLEAdvertisementFilter()
advertisement = BluetoothLEAdvertisement()
advertisement.local_name = 'FS-'
adv_filter.advertisement = advertisement

_is_scanning = False

_active_session_id = -1

def _on_btread_connect():
    print('BTreadDevice connected')

def _on_btread_disconnect():
    print('BTreadDevice disconnected')

def _on_btread_machine_status_change(data: FTMSMachineStatusEvent):
    global _active_session_id
    if data.event == FTMSMachineStatusEventOptions.START_RESUME and _active_session_id == -1:
        new_session = dbmanager.start_session()
        _active_session_id = new_session.SessionID
        asyncio.create_task(sio.emit('training:start'))
    if data.event == FTMSMachineStatusEventOptions.PAUSE_STOP:
        if _active_session_id == -1:
            print('No active session')
        else:
            dbmanager.finish_session(_active_session_id)
            _active_session_id = -1
            asyncio.create_task(sio.emit('training:end'))

def _on_btread_training_status_change(new_data: FTMSTrainingStatus, old_data: FTMSTrainingStatus):
    print(new_data)

def _on_btread_treadmill_data(new_data: FTMSTreadmillData, old_data: FTMSTreadmillData):
    global _active_session_id
    if _active_session_id > 0:
        d = dbmanager.new_datum(new_data.instantaneous_speed, new_data.elapsed_time, new_data.total_energy, new_data.total_distance, _active_session_id)
        asyncio.create_task(sio.emit('training:datum', DatumTableSchema().dump(d)))
    # print(new_data)

@sio.event
async def connect(sid: str, env: dict):
    print(f'Client connected, sid: {sid}')

@sio.event
async def disconnect(sid: str):
    print(f'Client disconnected, sid: {sid}')

@sio.on('state_sync')
async def sync_state(sid: str):
    global _device, _is_scanning, _scanned_devices, _active_session_id
    training_data_cur_session = dbmanager.get_session_datapoints(_active_session_id)
    state_obj = {
        'devices': {
                'device': {
                'address': _device.mac_address,
            } if _device else None,
            'isScanning': _is_scanning,
            'scannedDevices': _scanned_devices,
        },
        'training': {
            'status': 'idle' if _active_session_id == -1 else 'running',
            'data': [] if _active_session_id == -1 else DatumTableSchema().dump(training_data_cur_session, many=True)
        }
    }
    await sio.emit('state_sync', state_obj, sid)

@sio.on('ble:scan')
async def scan_devices(sid: str, args):
    global _is_scanning, _scanned_devices
    if _is_scanning:
        return
    _is_scanning = True
    devices = {}
    def on_device_found(dev: BLEDevice, adv: AdvertisementData):
        devices[dev.address] = {
            'address': dev.address,
            'name': dev.name,
            'rssi': dev.rssi
        }

    scanner = BleakScanner()
    scanner.set_scanning_filter(AdvertisementFilter=adv_filter)
    scanner.register_detection_callback(on_device_found)
    print(f'Starting ble scan at req of {sid}')
    await scanner.start()
    await asyncio.sleep(5)
    await scanner.stop()
    print(f'Stopped ble scan ({sid})')
    _is_scanning = False
    _scanned_devices = list(devices.values()),
    await sio.emit('ble:scan', list(devices.values()), sid)

@sio.on('ble:connect')
async def init_btread(sid: str, args):
    global _device
    (mac, ) = args
    _device = BTreadDevice(mac)
    _device.on(BTreadDeviceEvents.CONNECT, _on_btread_connect)
    _device.on(BTreadDeviceEvents.DISCONNECT, _on_btread_disconnect)
    _device.on(BTreadDeviceEvents.MACHINE_STATUS_CHANGED, _on_btread_machine_status_change)
    _device.on(BTreadDeviceEvents.TRAINING_STATUS_CHANGED, _on_btread_training_status_change)
    _device.on(BTreadDeviceEvents.TREADMILL_DATA_CHANGED, _on_btread_treadmill_data)
    result = await _device.connect()
    if result:
        await sio.emit('ble:connect', True, sid)
    else:
        await sio.emit('ble:connect', False, sid)
        await deinit_btread(sid)

@sio.on('ble:disconnect')
async def deinit_btread(sid: str, *args):
    print(args)
    global _device
    if _device:
        result = await _device.disconnect()
        if result is None:
            await sio.emit('ble:disconnect', 'Device not connected', sid)
        elif result is False:
            await sio.emit('ble:disconnect', 'Failed to disconnect?', sid)
        elif result:
            await sio.emit('ble:disconnect', 'Disconnected successfully', sid)
        _device = None

@sio.on('training:start')
async def training_start(sid: str, *args):
    global _device
    # try:
    await _device.start()
    await sio.emit('training:start', True, sid)
    # except Exception as e:
    #     print(1, e)
    #     await sio.emit('training:start', False, sid)

@sio.on('training:end')
async def training_end(sid: str, *args):
    global _device
    # try:
    await _device.stop()
    await sio.emit('training:end', True, sid)
    # except:
        # await sio.emit('training:end', False, sid)

async def main():
    await init_btread(-1, ('5A:B8:5E:20:B4:71',))
    while True:
        try:
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break
    await deinit_btread(-1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(deinit_btread(-1))