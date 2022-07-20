import asyncio
from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.service import BleakGATTService, BleakGATTServiceCollection
from bleak.backends.winrt.client import BLEDevice
from enum import Enum
from FTMS import FTMSControlPointCommand, FTMSControlPointEvent, FTMSMachineStatusEvent, FTMSSpeedRange, FTMSTrainingStatus, FTMSTreadmillData
import math
from pyee import EventEmitter
from utils import uuid_from_sid

class BTreadDeviceEvents(Enum):
    CONNECT = 'connect'
    TRAINING_STATUS_CHANGED = 'tStatChanged'
    # TRAINING_STATUS_ERROR = 'tStatErr'
    TREADMILL_DATA_CHANGED = 'tDataChanged'
    CONTROL_POINT_EVENT = 'cpCFM'
    MACHINE_STATUS_CHANGED = 'machStatChanged'
    DISCONNECT = 'disconnect'

class BTreadDevice(EventEmitter):

    mac_address = None
    __conn_attempts = None

    __device: BLEDevice = None
    __client: BleakClient = None
    __services: BleakGATTServiceCollection
    __ftms_service: BleakGATTService
    __ftms_control_point_c: BleakGATTCharacteristic
    __ftms_feature_c: BleakGATTCharacteristic
    __ftms_speed_range_c: BleakGATTCharacteristic
    __ftms_training_status_c: BleakGATTCharacteristic
    __ftms_treadmill_data_c: BleakGATTCharacteristic
    __ftms_machine_status_c: BleakGATTCharacteristic
    
    __training_status: FTMSTrainingStatus = None
    # __training_status_monitor_thread: Thread
    # __training_status_monitor_stop: Event

    __raw_treadmill_data: bytearray = bytearray()
    __treadmill_data: FTMSTreadmillData = None

    __speed_range: FTMSSpeedRange = None

    @property
    def training_status(self):
        return self.__training_status

    @property
    def speed_range(self):
        return self.__speed_range

    def __init__(self, mac_address, conn_attempts = 3):
        super().__init__()
        self.mac_address = mac_address
        self.__conn_attempts = conn_attempts
        # self.__training_status_monitor_stop = Event()

    async def connect(self):
        attempts = 0
        while attempts < self.__conn_attempts:
            try:
                self.__device = await BleakScanner.find_device_by_address(self.mac_address)
                if not self.__device:
                    raise Exception('Device not found.')
                else:
                    print('Device found')
                self.__client = BleakClient(self.__device)
                did_connect = await self.__client.connect()
                if not did_connect:
                    raise Exception('Connection attempt failed')
                self.__services = await self.__client.get_services()
                self.__ftms_service = self.__services.get_service(uuid_from_sid('1826'))
                self.__ftms_control_point_c = self.__ftms_service.get_characteristic(uuid_from_sid('2ad9'))
                self.__ftms_training_status_c = self.__ftms_service.get_characteristic(uuid_from_sid('2ad3'))
                self.__ftms_speed_range_c = self.__ftms_service.get_characteristic(uuid_from_sid('2ad4'))
                self.__ftms_treadmill_data_c = self.__ftms_service.get_characteristic(uuid_from_sid('2acd'))
                # self.__ftms_feature_c = self.__ftms_service.get_characteristic(uuid_from_sid('2acc'))
                self.__ftms_machine_status_c = self.__ftms_service.get_characteristic(uuid_from_sid('2ada'))
                # [IGNORE]  Despite TrainingStatusCharacteristic *saying* it supports notifications, this doesn't work
                #           await self.__client.start_notify(self.__ftms_training_status_c, self.__training_status_handler)
                # [/IGNORE]
                # !!! Adding the notify for treadmill_data_handler made the status handler work!
                await self.__client.start_notify(self.__ftms_machine_status_c, self.__machine_status_handler)
                await self.__client.start_notify(self.__ftms_treadmill_data_c, self.__treadmill_data_handler)
                await self.__client.start_notify(self.__ftms_training_status_c, self.__training_status_handler)
                await self.__client.start_notify(self.__ftms_control_point_c, self.__control_point_handler, force_indicate=True)
                # await self.__client.write_gatt_char(self.__ftms_control_point_c, bytearray((0,)), True)
                # features = await self.__client.read_gatt_char(self.__ftms_feature_c)
                default_training_status = await self.__client.read_gatt_char(self.__ftms_training_status_c)
                self.__training_status = FTMSTrainingStatus(default_training_status)
                # self.__training_status_monitor_thread = Thread(target=asyncio_threading_middleware, args=(self.__training_status_monitor,))
                # self.__training_status_monitor_thread.start()
                speed_range = await self.__client.read_gatt_char(self.__ftms_speed_range_c)
                self.__speed_range = FTMSSpeedRange(speed_range)
                self.emit(BTreadDeviceEvents.CONNECT)
                return True
            except Exception as e:
                print(e)
                attempts += 1
                await self.disconnect()
                await asyncio.sleep(3)
        return self.__client and self.__client.is_connected

    async def disconnect(self):
        if self.__client and self.__client.is_connected:
            disconnect_result = await self.__client.disconnect()
            if disconnect_result:
                # self.__training_status_monitor_stop.set()
                # self.__training_status_monitor_thread.join()
                self.__device = None
                self.__client = None
                self.__services = None
                self.__ftms_service = None
                self.__ftms_control_point_c = None
                self.__ftms_feature_c = None
                self.__ftms_speed_range_c = None
                self.__ftms_training_status_c = None
                self.__ftms_treadmill_data_c = None
                self.__training_status = None
                self.__raw_treadmill_data = bytearray()
                self.__treadmill_data = None
                self.__speed_range = None
                self.emit(BTreadDeviceEvents.DISCONNECT)
                return True
            else:
                return False
                print('Device failed to disconnect?')
        else:
            return None
            print('Not connected')

    def __machine_status_handler(self, sender: int, data: bytearray):
        self.emit(BTreadDeviceEvents.MACHINE_STATUS_CHANGED, FTMSMachineStatusEvent(data))

    def __training_status_handler(self, sender: int, data: bytearray):
        status = FTMSTrainingStatus(data)
        if self.__training_status is None:
            self.__training_status = status
            self.emit(BTreadDeviceEvents.TRAINING_STATUS_CHANGED, status, self.__training_status)
            return
        delta = status.__dict__.items() ^ self.__training_status.__dict__.items()
        if len(delta) > 0:
            self.emit(BTreadDeviceEvents.TRAINING_STATUS_CHANGED, status, self.__training_status)
            self.__training_status = status
        
    # async def __training_status_monitor(self):
    #     while not self.__training_status_monitor_stop.is_set():
    #         try:
    #             if self.__client and self.__client.is_connected:
    #                 result = await self.__client.read_gatt_char(self.__ftms_training_status_c)
    #                 print(result)
    #                 await asyncio.sleep(0.5)
    #             else:
    #                 print('Client not connected, exiting')
    #                 return
    #         except Exception as e:
    #             self.emit(BTreadDeviceEvents.TRAINING_STATUS_ERROR, e)
    #             return

    def __treadmill_data_handler(self, sender: int, data: bytearray):
        # print(data)
        if data != self.__raw_treadmill_data:
            new_data = FTMSTreadmillData(data)
            self.emit(BTreadDeviceEvents.TREADMILL_DATA_CHANGED, new_data, self.__treadmill_data)
            self.__raw_treadmill_data = data
            self.__treadmill_data = new_data

    async def __control_point_handler(self, sender, data):
        self.emit(BTreadDeviceEvents.CONTROL_POINT_EVENT, FTMSControlPointEvent(data))
        # return_c = self.__services.get_characteristic(sender)
        # await self.__client.write_gatt_char(return_c, b'\x1d')

    async def start(self):
        await self.__send_cmd(self.__ftms_control_point_c, bytearray((FTMSControlPointCommand.START_RESUME.value,)))

    async def stop(self):
        await self.__send_cmd(self.__ftms_control_point_c, bytearray((FTMSControlPointCommand.STOP_PAUSE.value, 0x01)))

    async def pause(self):
        await self.__send_cmd(self.__ftms_control_point_c, bytearray((FTMSControlPointCommand.STOP_PAUSE.value, 0x02)))

    async def set_speed(self, speed: float):
        new_target_speed = int(math.floor(speed * 100))
        await self.__send_cmd(self.__ftms_control_point_c, bytearray([FTMSControlPointCommand.SET_SPEED.value, new_target_speed]))
        
    async def __send_cmd(self, control_point: BleakGATTCharacteristic, bytes_to_send: bytearray):
        checksum = sum(bytes_to_send[1:]) & 0xFF
        bytes_to_send.append(checksum)
        await self.__client.write_gatt_char(control_point, bytes_to_send, True)