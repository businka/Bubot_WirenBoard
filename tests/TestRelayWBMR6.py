import asyncio
import logging
import unittest
from datetime import datetime

from bubot.core.TestHelper import wait_run_device, wait_cancelled_device
from bubot_modbus.buject.OcfDevice.subtype.SerialServerHF511.SerialServerHF511 import SerialServerHF511 as ModbusDevice
from bubot_wirenboard.buject.OcfDevice.subtype.RelayWBMR6C.RelayWBMR6C import RelayWBMR6C as Device

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger = logging.getLogger('Bubot_CoAP')
logger.setLevel(logging.ERROR)


class TestRelayWBMR6C(unittest.IsolatedAsyncioTestCase):
    net_interface = "192.168.1.11"
    config = {
        '/oic/con': {
            'master': dict(),
            'slave': 0x6f,
            'baudRate': 9600,
            'parity': 'None',
            'dataBits': 8,
            'stopBits': 2,
            'udpCoapIPv6': None
        }

    }
    bad_ip_config = {
        "/oic/d": {
            "di": "1"
        },
        "/oic/con": {
            "master": {
                # "anchor": "ocf://6d350e5d-8b7c-459e-a671-e5860b318796",
                "di": "6d350e5d-8b7c-459e-a671-e5860b318796",
                "href": "/modbus_msg",
                "eps": [
                    {
                        "ep": "coap://192.168.1.11:61169",
                        "net_interface": "192.168.1.11"
                    }
                ]
            },
            "slave": 113
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
            'udpCoapIPv4': True,
            'udpCoapIPv6': False
        }
    }

    async def asyncSetUp(self) -> None:
        self.modbus_device = ModbusDevice.init_from_file(di='2')
        self.modbus_task = await wait_run_device(self.modbus_device)
        self.config['/oic/con']['master']['anchor'] = self.modbus_device.link['anchor']
        self.config['/oic/con']['master']['eps'] = self.modbus_device.link['eps']
        self.config['/oic/con']['master']['eps'][0]['net_interface'] = self.net_interface
        self.device = Device.init_from_config(self.config, di='1')
        self.device_task = await wait_run_device(self.device)

    async def asyncTearDown(self) -> None:
        await wait_cancelled_device(self.device, self.device_task)
        await wait_cancelled_device(self.modbus_device, self.modbus_task)

    async def test_update_switch(self):
        number = 1
        value = False
        result1 = (await self.device.retrieve_switch(number))['value']
        result2 = (await self.device.update_switch(number, not result1))['value']
        result3 = (await self.device.retrieve_switch(number))['value']
        self.assertEqual(result3, not result1)
        result4 = (await self.device.update_switch(number, result1))['value']
        result5 = (await self.device.retrieve_switch(number))['value']
        self.assertEqual(result5, result1)

    async def test_retrieve_model(self):
        res = await self.device.modbus.is_device()
        self.assertTrue(res)

    async def test_maximum_load(self):
        task = []
        for i in range(50):
            task.append(self.device.retrieve_switch(1))
        begin = datetime.now()
        result = await asyncio.gather(*task)
        end = datetime.now()
        print(end - begin)

    async def test_find_devices(self):
        res = await self.device.find_devices(notify=notify)
        pass


async def notify(data):
    print(data)
