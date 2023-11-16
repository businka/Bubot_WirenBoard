import asyncio
# from aio_modbus_client.TransportSerial import TransportSerial as Modbus
# from aio_modbus_client.ModbusProtocolRtuHF5111 import ModbusProtocolRtuHF5111 as Protocol
# from aio_modbus_client.ModbusProtocolRtu import ModbusProtocolRtu as Protocol
# from aio_modbus_client.ModbusProtocolRtu import ModbusProtocolRtu as Protocol
import logging
import socket
import unittest

from aio_modbus_client.ModbusProtocolRtuHF5111 import ModbusProtocolRtuHF5111 as Protocol
from aio_modbus_client.TransportSocket import TransportSocket as Modbus
from .DimmerWBLED import DimmerWBLED as Device


class TestDimmerWBLED(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.ERROR)
        # 130 спальня 134 столовая  114 кухня 113 кабинет 105 туалет
        device_address = 191
        address = ('192.168.1.25', 502)
        cls.device = Device(device_address, Protocol(Modbus(host=address[0], port=address[1])))
        # cls.url = 'COM5'
        # cls.device = Device(device_address, Protocol(Modbus(host='COM5')))

    def setUp(self):
        pass

    async def asyncTearDown(self):
        await self.device.close()

    async def test_scan(self):
        # address = ('192.168.1.25', 502)
        # if await self.device.is_device():
        #     print('check')
        self.device.protocol.timeout = 0.4
        for i in range(254):
            self.device.slave_id = i
            await asyncio.sleep(0.2)
            try:
                await self.device.is_device()
            except TimeoutError:
                pass

        pass

    async def test_write_adress(self):
        old_slave_id = 0x8d
        new_slave_id = 0x94
        self.device.protocol.timeout = 0.3
        self.device.slave_id = old_slave_id
        result = await self.device.write_param('slave_id', new_slave_id)

        pass

    async def test_read_brightness_blue(self):
        result = await self.device.read_param('level_blue')
        print(result)
        result = await self.device.read_param('color')
        print(result)
        pass

    def test_write_brightness_blue(self):
        # self.device.modbus = ModbusTcpChinaGarbage(self.address, framer=ModbusFramer)
        result = self.device.write_param('level_green', 0)
        pass

    async def test_color(self):
        color = [0, 0, 0]
        # color = [255, 255, 255]
        await self.device.write_param('color', color)
        self.assertEqual(self.device.data['color'], color)
        result = await self.device.read_param('color')
        self.assertEqual(result, color)
        self.assertEqual(self.device.data['color'], color)

    async def test_power(self):
        power1 = await self.device.read_param('power_rgb')
        await self.device.write_param('power_rgb', not power1)
        power2 = await self.device.read_param('power_rgb')
        self.assertEqual(not power1, power2)
        await self.device.write_param('power_rgb', power1)
        power3 = await self.device.read_param('power_rgb')
        self.assertEqual(power1, power3)

    async def test_brightness(self):
        # color = [255, 255, 255]
        # brightness = 5
        # value = await self.device.read_param('brightness_4w')
        # voltage = await self.device.read_param('current_supply_voltage')
        # input1_short_press_action = await self.device.read_param('input1_short_press_action')
        # input1_long_press_action = await self.device.read_param('input1_long_press_action')
        # # await self.device.write_param('reboot', 1)
        # red = await self.device.read_param('level_red')
        # green = await self.device.read_param('level_green')
        # blue = await self.device.read_param('level_blue')
        # res = await self.device.write_param('level_red', 255)
        # res = await self.device.write_param('level_green', 255)
        # res = await self.device.write_param('level_blue', 255)
        # power1 = await self.device.read_param('power_rgb')
        res = await self.device.write_param('power_rgb', False)
        res = await self.device.write_param('power_4w', True)
        # value2 = await self.device.read_param('power_rgb')
        await asyncio.sleep(1)
        pass
        # self.assertEqual(self.device.data['power'], False)
        # result = self.device.read_param('brightness')
        # self.assertEqual(result, 100)

        # self.device.write_param('power', True)
        await self.device.write_param('brightness', brightness)
        pass
        result = self.device.read_param('brightness')
        pass
        # self.assertEqual(self.device.data['power'], False)
        pass

        # self.device.write_param('brightness', 20)
        # self.device.write_param('brightness', 40)
        # self.device.write_param('brightness', 60)
        # self.device.write_param('brightness', 80)
        # self.device.write_param('brightness', 100)
        # self.assertEqual(self.device.data['brightness'], brightness)
        # self.assertEqual(result, brightness)
        # result = self.device.write_param('power', False)
        # self.device.write_param('brightness', brightness)
        # result = self.device.read_param('brightness')
        # result = self.device.write_param('power', True)
        # self.assertEqual(self.device.data['color'], color)

    async def test_get_version(self):
        value = await self.device.read_param('version')
        print(value)
        pass
        # self.assertEqual(100, result)

    async def test_read_model(self):
        # self.device.modbus.connect()
        value = await self.device.read_param('model')
        self.assertEqual('WB-MRGBW-D', value.replace('\x00', ''))
        print(value)

    async def test_get_power_all(self):
        value = await self.device.read_param('power_4w')
        print(value)
        pass

    async def test_read_button_mode(self):
        for i in [0x90, 0x91, 0x92, 0x93, 0x94, 0x95, 0x96]:
            self.device.slave_id = i
            # await self.device.write_param('button_mode', 0)
            await self.device.write_param('dimmer', 100)
        # self.device.modbus.connect()
        # value = await self.device.write_param('button_mode', 0)
        # self.assertEqual(value, 'WBMRGB')
        # print(value)

    async def test_find(self):
        value = await self.device.find_devices(0x8F, 0x97)
        print(value)
        self.assertEqual(len(value), 7)

    async def test_id_device(self):
        # self.device.modbus.connect()
        self.device.protocol.timeout = 0.7
        value = await self.device.is_device()
        self.assertEqual(value, True)
        print(value)

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
