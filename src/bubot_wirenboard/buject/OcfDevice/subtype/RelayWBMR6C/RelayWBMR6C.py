from bubot_modbus.buject.OcfDevice.subtype.ModbusSlave.ModbusSlave import ModbusSlave
from bubot_helpers.ExtException import ExtTimeoutError
from bubot_wirenboard import __version__ as device_version
from .lib.WirenBoardRelay import WirenBoardRelay as ModbusDevice
from .OicRSwitchBinary import OicRSwitchBinary
# import logging

# _logger = logging.getLogger(__name__)


class RelayWBMR6C(ModbusSlave):
    ModbusDevice = ModbusDevice
    version = device_version
    template = False
    file = __file__

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for num in range(6):
            self.resource_layer.add_handler(f'/switch/{num + 1}', OicRSwitchBinary)

    async def retrieve_switch(self, number):
        res = await self.modbus.read_param(f'switch_{number}')
        self.set_param(f'/switch/{number}', 'value', res)
        return self.get_param(f'/switch/{number}')

    async def update_switch(self, number, value):
        if value is not None:
            try:
                res = await self.modbus.write_param(f'switch_{number}', value)
                self.set_param(f'/switch/{number}', 'value', value)
                return self.get_param(f'/switch/{number}')
            except KeyError:
                pass
            except Exception as err:
                self.log.error(err)

    async def on_idle(self):
        try:
            for i in range(6):
                await self.retrieve_switch(i + 1)
        except ExtTimeoutError:
            self.log.info("Timeout, change state to 'pending'")
            self.set_param('/oic/mnt', 'currentMachineState', 'pending', save_config=True)
        except Exception as err:
            self.log.error(err)
