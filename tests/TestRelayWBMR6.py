import unittest
from BubotObj.OcfDevice.subtype.RelayWBMR6C.RelayWBMR6C import RelayWBMR6C as Device
from BubotObj.OcfDevice.subtype.SerialServerHF511.SerialServerHF511 import SerialServerHF511 as ModbusDevice
from Bubot.Core.OcfMessage import OcfRequest
from Bubot.Core.TestHelper import async_test, wait_run_device, get_config_path, wait_cancelled_device
import logging
import asyncio
from datetime import datetime


class TestRelayWBMR6C(unittest.TestCase):
    pass
    config = {
        '/oic/con': {
            'master': dict(),
            'slave': 0x6f,
            'baudRate': 9600,
            'parity': 'None',
            'dataBits': 8,
            'stopBits': 2,
            'udpCoapPort': 17771,
            'udpCoapIPv4': False,
            'udpCoapIPv6': True
        }

    }
    modbus_config = {
        '/oic/con': {
            'host': '192.168.1.25',
            'port': 502,
            'baudRate': 9600,
            'parity': 0,
            'dataBits': 8,
            'stopBits': 2,
            'udpCoapPort': 17772,
            'udpCoapIPv4': False,
            'udpCoapIPv6': True
        }
    }
    @async_test
    async def setUp(self, **kwargs):
        logging.basicConfig(level=logging.DEBUG)
        self.config_path = get_config_path(__file__)

    @async_test
    async def test_get_update_switch(self):
        number = 1
        value = False
        modbus_device = ModbusDevice.init_from_config(self.modbus_config, path=self.config_path)
        mobus_task = await wait_run_device(modbus_device)
        self.config['/oic/con']['master'] = modbus_device.link
        self.device = Device.init_from_config(self.config, path=self.config_path)
        device_task = await wait_run_device(self.device)
        message = OcfRequest(op='update', to=dict(href='/switch/{}'.format(number)), cn=dict(value=value))
        result = await self.device.on_post_request(message)
        self.assertEqual(result['value'], value)

    @async_test
    async def test_get_retrieve_switch(self):
        number = 1
        value = False
        modbus_device = ModbusDevice.init_from_config(self.modbus_config, path=self.config_path)
        mobus_task = await wait_run_device(modbus_device)
        self.config['/oic/con']['master'] = modbus_device.link
        self.device = Device.init_from_config(self.config, path=self.config_path)
        device_task = await wait_run_device(self.device)
        message = OcfRequest(op='retrieve', to=dict(href='/switch/{}'.format(number)))
        result = await self.device.on_post_request(message)
        self.assertEqual(result['value'], value)

    @async_test
    async def test_get_retrieve_model(self):
        modbus_device = ModbusDevice.init_from_config(self.modbus_config, path=self.config_path)
        mobus_task = await wait_run_device(modbus_device)
        self.config['/oic/con']['master'] = modbus_device.link
        self.device = Device.init_from_config(self.config, path=self.config_path)
        device_task = await wait_run_device(self.device)
        res = await self.device.modbus.is_device()
        self.assertTrue(res)

    @async_test
    async def test_retrieve_switch(self):
        number = 1
        value = False
        modbus_device = ModbusDevice.init_from_config(self.modbus_config, path=self.config_path)
        mobus_task = await wait_run_device(modbus_device)
        self.config['/oic/con']['master'] = modbus_device.link
        self.device = Device.init_from_config(self.config, path=self.config_path)
        device_task = await wait_run_device(self.device)

        tasks = []
        for i in range(16):
            message = OcfRequest(op='retrieve', to=dict(href='/switch/{}'.format(number)))
            tasks.append(self.device.on_post_request(message))
        res = await asyncio.gather(*tasks)
        pass

    @async_test
    async def test_maximum_load(self):
        modbus_device = ModbusDevice.init_from_file('SerialServerHF511', '2')
        modbus_task = await wait_run_device(modbus_device)
        self.config['/oic/con']['master']['anchor'] = modbus_device.link['anchor']
        self.config['/oic/con']['master']['eps'] = modbus_device.link['eps']
        device = Device.init_from_config(self.config, path=self.config_path)
        device_task = await wait_run_device(device)
        task = []
        count = 50
        for i in range(50):
            message = OcfRequest(op='retrieve', to=dict(href='/switch/1'))
            task.append(device.on_get_request(message))
        begin = datetime.now()
        result = await asyncio.gather(*task)
        end = datetime.now()
        print(end - begin)
        await wait_cancelled_device(device, device_task)
        await wait_cancelled_device(modbus_device, modbus_task)
