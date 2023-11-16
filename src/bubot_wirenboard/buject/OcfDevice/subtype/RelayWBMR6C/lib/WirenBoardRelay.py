import logging

from aio_modbus_client.ModbusDevice import ModbusDevice

_logger = logging.getLogger(__name__)


class WirenBoardRelay(ModbusDevice):
    file = __file__

    async def is_device(self):
        result = await self.read_param('model')
        if result:
            _logger.debug(f'WirenBoardRelay is_device read 0x{self.slave_id:x} {result}')
        if result in ['WBMR6C']:
            return True
        return False
