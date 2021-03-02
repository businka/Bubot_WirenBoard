from BubotObj.OcfDevice.subtype.ModbusSlave.ModbusSlave import ModbusSlave
from BubotObj.OcfDevice.subtype.DimmerWBMRGBWD import __version__ as device_version
from Bubot.Helpers.Helper import Helper
from .lib.WirenBoardDimmer import WirenBoardDimmer as ModbusDevice
# import logging

# _logger = logging.getLogger(__name__)


class DimmerWBMRGBWD(ModbusSlave):
    ModbusDevice = ModbusDevice
    version = device_version
    template = False
    file = __file__

    async def update_res(self):
        self.set_param('/brightness', 'rgbValue', self.modbus.data['brightness'])
        self.set_param('/color', 'rgbValue', self.modbus.data['color'])
        self.set_param('/power', 'value', self.modbus.data['power'])

    async def on_retrieve_power(self, message):
        await self.modbus.read_param('power')
        await self.update_res()
        return self.get_param('/power')

    async def _update_main_res(self, param, message, modbus_param=None):
        try:
            modbus_param = modbus_param if modbus_param else param
            await self.modbus.read_param('power')
            value = message.cn[param]
            if value is not None and value != self.modbus.data[modbus_param]:
                await self.modbus.write_param(modbus_param, value)
            await self.update_res()
        except KeyError:
            pass
        return self.get_param('/{}'.format(modbus_param))

    async def on_update_power(self, message):
        return await self._update_main_res('value', message, 'power')

    async def on_update_brightness(self, message):
        return await self._update_main_res('brightness', message)

    async def on_update_color(self, message):
        return await self._update_main_res('color', message)

    async def on_idle(self):
        try:
            await self.modbus.read_param('power')
            await self.update_res()
        except Exception as err:
            self.log.error(err)
