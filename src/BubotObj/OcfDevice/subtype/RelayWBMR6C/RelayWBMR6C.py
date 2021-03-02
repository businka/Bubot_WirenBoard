from BubotObj.OcfDevice.subtype.ModbusSlave.ModbusSlave import ModbusSlave
from BubotObj.OcfDevice.subtype.RelayWBMR6C import __version__ as device_version
from .lib.WirenBoardRelay import WirenBoardRelay as ModbusDevice
# import logging

# _logger = logging.getLogger(__name__)


class RelayWBMR6C(ModbusSlave):
    ModbusDevice = ModbusDevice
    version = device_version
    template = False
    file = __file__

    async def on_retrieve_switch(self, number, message):
        res = await self.modbus.read_param('switch_{}'.format(number))
        self.set_param('/switch/{}'.format(number), 'value', res)
        return self.get_param('/switch/{}'.format(number))

    async def on_update_switch(self, number, message):
        value = message.cn.get('value')
        if value is not None:
            try:
                value = message.cn['value']
                await self.modbus.write_param('switch_{}'.format(number), value)
            except KeyError:
                pass
            except Exception as err:
                self.log.error(err)
        self.update_param('/switch/{}'.format(number), None, message.cn)
        return self.get_param('/switch/{}'.format(number))

    async def on_retrieve_switch_1(self, message):
        return await self.on_retrieve_switch(1, message)

    async def on_retrieve_switch_2(self, message):
        return await self.on_retrieve_switch(2, message)

    async def on_retrieve_switch_3(self, message):
        return await self.on_retrieve_switch(3, message)

    async def on_retrieve_switch_4(self, message):
        return await self.on_retrieve_switch(4, message)

    async def on_retrieve_switch_5(self, message):
        return await self.on_retrieve_switch(5, message)

    async def on_retrieve_switch_6(self, message):
        return await self.on_retrieve_switch(6, message)

    async def on_update_switch_1(self, message):
        return await self.on_update_switch(1, message)

    async def on_update_switch_2(self, message):
        return await self.on_update_switch(2, message)

    async def on_update_switch_3(self, message):
        return await self.on_update_switch(3, message)

    async def on_update_switch_4(self, message):
        return await self.on_update_switch(4, message)

    async def on_update_switch_5(self, message):
        return await self.on_update_switch(5, message)

    async def on_update_switch_6(self, message):
        return await self.on_update_switch(6, message)

    async def on_idle(self):
        try:
            for i in range(6):
                number = i + 1
                res = await self.modbus.read_param('switch_{}'.format(number))
                self.set_param('/switch/{}'.format(number), 'value', res)
        except Exception as err:
            self.log.error(err)
