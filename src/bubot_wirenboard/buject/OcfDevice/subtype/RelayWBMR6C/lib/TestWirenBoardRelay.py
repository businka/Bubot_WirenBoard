import asyncio
import inspect
# from aio_modbus_client.ModbusProtocolTcp import ModbusProtocolTcp as Protocol
# from aio_modbus_client.ModbusProtocolRtu import ModbusProtocolRtu as Protocol
import logging
import socket
import unittest

from aio_modbus_client.ModbusProtocolRtuHF5111 import ModbusProtocolRtuHF5111 as Protocol
from aio_modbus_client.TransportSocket import TransportSocket as Modbus
from .WirenBoardRelay import WirenBoardRelay as Device


def async_test(f):
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        # kwargs['loop'] = loop
        if inspect.iscoroutinefunction(f):
            future = f(*args)
        else:
            coroutine = asyncio.coroutine(f)
            future = coroutine(*args, **kwargs)
        loop.run_until_complete(future)

    return wrapper


class TestWirenBoardRelay(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.ERROR)
        device_address = 111
        address = ('192.168.1.25', 502)
        cls.device = Device(device_address, Protocol(Modbus(host=address[0], port=address[1])))

    def setUp(self):
        pass

    @async_test
    async def test_switch(self):
        # self.device.modbus = ModbusTcpChinaGarbage(self.address, framer=ModbusFramer)
        # await self.device.write_param('switch_2', True)
        result = await self.device.read_param('switch_1')
        # self.assertEqual(result, True)
        # await self.device.write_param('switch_2', False)
        # result = await self.device.read_param('switch_2')
        # self.assertEqual(result, False)
        pass

    def test_get_version(self):
        value = self.device.read_param('version')
        print(value)
        pass
        # self.assertEqual(100, result)

    @async_test
    async def test_read_model(self):
        # self.device.modbus.connect()
        value = await self.device.read_param('model')
        self.assertEqual(value, 'WBMR6C')
        print(value)

    @async_test
    async def test_find(self):
        value = await self.device.find_devices(0x6a, 0x6f)
        self.assertEqual(len(value), 3)
        print(value)

    def test_id_device(self):
        # self.device.modbus.connect()
        self.device.modbus.timeout = 0.5
        value = self.device.is_device()
        self.assertEqual(value, True)
        print(value)

    def test_pymodbus(self):
        client = ModbusTcpHF5111('192.168.1.25', framer=ModbusFramer)
        result = client.read_input_registers(200, 6, unit=self.device_address)
        print(result)
        # result = client.read_holding_registers(200, 6, unit=self.device_address)
        # result = client.read_holding_registers(200, 6, unit=self.device_address)
        # print(result.bits[0])
        client.close()

    def test_simple(self):
        sock = socket.socket()
        sock.connect(self.address)
        # data = b'\x01\x03\x00\x00\x00\x06\x82\x04\x00\xc8\x00\x06'
        # sock.send(data)
        # print(sock.recv(1900))
        data = b'\x82\x04\x00\xc8\x00\x06\xee\x05'
        sock.send(data)
        print(sock.recv(1900))
        sock.close()
        pass
