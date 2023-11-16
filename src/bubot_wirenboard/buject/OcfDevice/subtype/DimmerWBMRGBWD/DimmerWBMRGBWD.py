from bubot_modbus.buject.OcfDevice.subtype.ModbusSlave.ModbusSlave import ModbusSlave
from bubot_helpers.ExtException import ExtTimeoutError
from bubot_wirenboard import __version__ as device_version
from .lib.WirenBoardDimmer import WirenBoardDimmer as ModbusDevice
from .OicRSwitchBinary import OicRSwitchBinary
# import logging

# _logger = logging.getLogger(__name__)


class DimmerWBMRGBWD(ModbusSlave):
    ModbusDevice = ModbusDevice
    version = device_version
    template = False
    file = __file__

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resource_layer.add_handler(f'/power', OicRSwitchBinary)

    async def update_res(self):
        self.set_param('/brightness', 'rgbValue', self.modbus.data['brightness'])
        self.set_param('/color', 'rgbValue', self.modbus.data['color'])
        self.set_param('/power', 'value', self.modbus.data['power'])

    async def power_retrieve(self):
        result = await self.modbus.read_param('power')
        await self.update_res()
        return self.get_param('/power')

    async def _update_main_res(self, param, value, modbus_param=None):
        try:
            modbus_param = modbus_param if modbus_param else param
            # await self.modbus.read_param('power')
            if value is not None and value != self.modbus.data[modbus_param]:
                await self.modbus.write_param(modbus_param, value)
            await self.update_res()
        except KeyError:
            pass
        return self.get_param('/{}'.format(modbus_param))

    async def power_update(self, value):
        return await self._update_main_res('value', value, 'power')

    async def brightness_update(self, value):
        return await self._update_main_res('brightness', value)

    async def color_update(self, value):
        return await self._update_main_res('color', value)

    async def on_idle(self):
        try:
            await self.power_retrieve()
        except Exception as err:
            self.log.error(err)
