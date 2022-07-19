# Based in part from https://developer.huawei.com/consumer/en/doc/development/HMSCore-Guides/ftms-list-0000001055208574

from enum import Enum

class FTMSSpeedRange:

    min_speed = 0
    max_speed = 0
    min_increment = 0

    def __init__(self, val: bytearray):
        ival = int.from_bytes(val, 'little')
        self.min_speed = ival >> 32
        self.max_speed = (ival & 0x0000FFFF0000) >> 16
        self.min_increment = ival & 0xFFFF

    def __str__(self):
        return f'[Speed Range]: Min: {self.min_speed}, Max: {self.max_speed}, Inc: {self.min_increment}'

    def __repr__(self):
        return f'FTMSSpeedRange({self.min_speed}, {self.max_speed}, {self.min_increment})'

class FTMSTrainingStatusOption(Enum):
    OTHER = 0
    IDLE = 1
    RUNNING = 0x0D
    PRE_WORKOUT = 0x0E
    POST_WORKOUT = 0x0F

class FTMSTrainingStatus:

    training_status_exists = False
    training_status_string_exists = False
    training_status = FTMSTrainingStatusOption.OTHER
    training_status_string = ''

    def __init__(self, val: bytearray):
        ival = int.from_bytes(val, 'little')
        self.training_status_exists = (ival & 0x01) == 1
        self.training_status_string_exists = (ival >> 1) & 0x01 == 1
        if self.training_status_exists:
            self.training_status = FTMSTrainingStatusOption((ival >> 8) & 0xFF)
        if self.training_status_string_exists:
            self.training_status_string = str(val[1:])

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'FTMSTrainingStatus({self.training_status_exists}, {self.training_status_string_exists}, {self.training_status.name}, {self.training_status_string})'

class FTMSTreadmillData:

    instantaneous_speed = 0
    # average_speed = None
    total_distance = 0
    # inclination = None
    # ramp_angle_setting = None
    # positive_elevation_gain = None
    # negative_elevation_gain = None
    # instantaneous_pace = None
    # average_pace = None
    total_energy = 0
    # energy_per_hour = None
    # energy_per_minute = None
    # heart_rate = None
    # metabolic_equivalent = None
    elapsed_time = 0
    # remaining_time = None
    # force_on_belt = None
    # power_output = None

    def __init__(self, val):
        self.instantaneous_speed = int.from_bytes(val[2:4], 'little') / 100.0
        self.total_distance = int.from_bytes(val[4:6], 'little')
        self.total_energy = int.from_bytes(val[6:8], 'big')
        self.elapsed_time = int.from_bytes(filter(lambda x: x != 0, val[8:]), 'little')

    def __repr__(self):
        return f'FTMSTreadmillData({self.instantaneous_speed}, {self.total_distance}, {self.total_energy}, {self.elapsed_time}'

    def __str__(self):
        return f'{self.instantaneous_speed} km/h, {self.total_distance} m, {self.total_energy} kcal, {self.elapsed_time} s'

class FTMSMachineStatusEventOptions(Enum):
    RFU = 0x00
    RESET = 0x01
    PAUSE_STOP = 0x02
    SAFETY_STOP = 0x03
    START_RESUME = 0x04
    SPEED_CHANGED = 0x05
    INCLINE_CHANGED = 0x06
    RESISTANCE_CHANGED = 0x07

class FTMSMachineStatusEvent:

    event: FTMSMachineStatusEventOptions = None
    param = None

    def __init__(self, val: bytearray):
        self.event = FTMSMachineStatusEventOptions(val[0])
        self.param = val[1:]

    def __repr__(self):
        return f'FTMSMachineStatusEvent({self.event.name}, {self.param})'

    def __str__(self):
        return self.__repr__()

class FTMSControlPointCommand(Enum):
    REQUEST_CONTROL = 0x00
    RESET = 0x01
    SET_SPEED = 0x02
    SET_INCLINE = 0x03
    SET_RESISTANCE = 0x04
    SET_POWER = 0x05
    START_RESUME = 0x07
    STOP_PAUSE = 0x08

class FTMSControlPointResult(Enum):
    SUCCESS = 0x01
    NOT_SUPPORTED = 0x02
    INCORRECT_PARAMETER = 0x03
    OPERATION_FAILED = 0x04
    CONTROL_NOT_ALLOWED = 0x05

class FTMSControlPointEvent:

    command: FTMSControlPointCommand
    result: FTMSControlPointResult
    param = None

    def __init__(self, val: bytearray):
        if val[0] != 0x80:
            raise Exception('Invalid control point event payload')
        self.command = FTMSControlPointCommand(val[1])
        self.result = FTMSControlPointResult(val[2])
        self.param = val[3:]

    def __repr__(self):
        return f'FTMSControlPointEvent({self.command.name}, {self.result.name}, {self.param})'
    
    def __str__(self):
        return self.__repr__()